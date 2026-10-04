"""Lino ThreatScan —— 命令行入口。"""
from __future__ import annotations

import argparse
from pathlib import Path

from .db import ThreatDB
from .scanner import Scanner

DEFAULT_DB = Path(__file__).resolve().parent.parent / "signatures" / "builtin.json"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="threatscan", description="Lino 威胁扫描器（安全层·审查闸门）。"
    )
    p.add_argument("--db", default=str(DEFAULT_DB), help="签名库 JSON 路径")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("selftest", help="用 EICAR 测试签名自检，验证扫描链路")

    s = sub.add_parser("scan", help="扫描一个文件或目录")
    s.add_argument("path")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    db = ThreatDB.load(args.db)
    scanner = Scanner(db)

    if args.command == "selftest":
        if scanner.selftest():
            print("自检通过：正确检出 EICAR 测试签名")
            return 0
        print("自检失败：未能检出 EICAR 签名，请检查签名库")
        return 1

    if args.command == "scan":
        path = Path(args.path)
        if path.is_dir():
            targets = sorted(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            targets = [path]
        else:
            print(f"错误：路径不存在或非文件/目录：{path}")
            return 1

        hits = 0
        for f in targets:
            try:
                verdict = scanner.scan_file(f)
            except OSError as exc:
                print(f"[跳过] {f}  →  {exc}")
                continue
            if verdict.malicious:
                hits += 1
                print(f"[恶意] {f}  →  {verdict.hit_name} ({verdict.hash})")
            else:
                print(f"[干净] {f}")

        print(f"扫描完成：{len(targets)} 个文件，命中 {hits} 个威胁")
        return 2 if hits else 0

    return 0