"""Lino App Installer —— 命令行入口。"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from . import __version__
from .backend import Backend
from .registry import Registry
from .schema import App

DEFAULT_INDEX = Path(__file__).resolve().parent.parent / "repo" / "index.json"
SUPPORTED_BACKENDS = {"flatpak"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lino-app",
        description="Lino App Installer —— 统一应用安装器（统一格式 + 沙箱 + 免终端）。",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--index", default=str(DEFAULT_INDEX), help="仓库索引 index.json 的路径")
    p.add_argument("-y", "--yes", action="store_true", help="跳过权限确认，直接继续")
    sub = p.add_subparsers(dest="command", required=True)

    q = sub.add_parser("search", help="按关键词搜索 Lino 应用仓库")
    q.add_argument("query")

    sub.add_parser("list", help="列出已安装的应用")

    i = sub.add_parser("info", help="查看应用详情与权限")
    i.add_argument("app")

    ins = sub.add_parser("install", help="安装一个或多个应用")
    ins.add_argument("apps", nargs="+")
    ins.add_argument(
        "--preflight-scan",
        metavar="PATH",
        help="安装前对本地包做威胁扫描，命中即拦截（默认命令 python -m threatscan）",
    )

    rm = sub.add_parser("remove", help="卸载一个或多个应用")
    rm.add_argument("apps", nargs="+")

    up = sub.add_parser("update", help="更新应用（不指定则更新全部）")
    up.add_argument("apps", nargs="*")

    return p


def _resolve(registry: Registry, app_id: str) -> App:
    try:
        return registry.get(app_id)
    except LookupError as exc:
        raise SystemExit(f"错误：{exc}") from exc


def _require_backend(backend: Backend, app: App) -> None:
    if app.backend not in SUPPORTED_BACKENDS:
        raise SystemExit(
            f"错误：应用 {app.id} 的后端「{app.backend}」尚未实现（规划中），"
            f"当前支持: {', '.join(sorted(SUPPORTED_BACKENDS))}。"
        )
    if not backend.available():
        raise SystemExit("错误：未找到 flatpak，请先安装（https://flatpak.org/）。")


def _confirm_permissions(app: App, assume_yes: bool) -> bool:
    if not app.permissions:
        return True
    print(f"「{app.name}」申请的权限：")
    for perm in app.permissions:
        print(f"  - {perm}")
    if assume_yes:
        print("  （--yes 已跳过确认）")
        return True
    answer = input("是否授权并继续安装？[y/N] ").strip().casefold()
    return answer in ("y", "yes")


def _print_app(app: App) -> None:
    star = " ★" if app.recommended else ""
    print(f"{app.id:<26} {app.name} [{app.category}]{star}")
    print(f"    {app.summary}")


def _preflight_scan(path: str) -> int:
    """调用外部威胁扫描器（ThreatScan）扫描本地包，透明返回其退出码。

    fail-closed 由调用方负责：此处仅透传，非 0 即视为威胁或扫描器异常，予以拦截。
    """
    cmd = os.environ.get("LINO_THREATSCAN_CMD", "python -m threatscan")
    return subprocess.run([*cmd.split(), "scan", path], check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = Registry.load(args.index)
    backend = Backend()

    if args.command == "search":
        results = registry.search(args.query)
        if not results:
            print(f"未在 Lino 仓库中找到「{args.query}」")
            return 0
        for app in results:
            _print_app(app)
        return 0

    if args.command == "info":
        app = _resolve(registry, args.app)
        print(f"应用：{app.name} ({app.id})")
        print(f"分类：{app.category}")
        print(f"简介：{app.summary}")
        if app.description:
            print(f"说明：{app.description}")
        print(f"后端：{app.backend}  ·  来源：{app.remote}  ·  ref：{app.ref}")
        print("权限：" + ("、".join(app.permissions) if app.permissions else "无（沙箱内运行）"))
        return 0

    if args.command == "list":
        if not backend.available():
            raise SystemExit("错误：未找到 flatpak，请先安装（https://flatpak.org/）。")
        installed = backend.list_installed()
        if not installed:
            print("尚未安装任何应用。")
            return 0
        for ref in installed:
            app = registry.by_ref(ref)
            print(f"{app.name} ({app.id})" if app else ref)
        return 0

    if args.command == "install":
        if args.preflight_scan and _preflight_scan(args.preflight_scan) != 0:
            print("检测到威胁（或扫描器异常），已按 fail-closed 拦截安装。")
            return 2
        for app_id in args.apps:
            app = _resolve(registry, app_id)
            _require_backend(backend, app)
            if backend.is_installed(app.ref):
                print(f"已安装：{app.name}")
                continue
            if not _confirm_permissions(app, args.yes):
                print(f"已取消：{app.name}")
                continue
            print(f"正在安装 {app.name} …")
            rc = backend.install(app.remote, app.ref, assume_yes=args.yes)
            print("✓ 安装完成" if rc == 0 else f"✗ 安装失败（退出码 {rc}）")
        return 0

    if args.command == "remove":
        for app_id in args.apps:
            app = _resolve(registry, app_id)
            _require_backend(backend, app)
            rc = backend.remove(app.ref, assume_yes=args.yes)
            print("✓ 已卸载" if rc == 0 else f"✗ 卸载失败（退出码 {rc}）")
        return 0

    if args.command == "update":
        if not args.apps:
            rc = backend.update(assume_yes=args.yes)
            print("✓ 更新完成" if rc == 0 else f"✗ 更新失败（退出码 {rc}）")
            return rc
        for app_id in args.apps:
            app = _resolve(registry, app_id)
            _require_backend(backend, app)
            rc = backend.update(app.ref, assume_yes=args.yes)
        return 0

    return 0