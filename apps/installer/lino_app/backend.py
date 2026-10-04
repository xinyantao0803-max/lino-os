"""Flatpak 适配层：把 Lino 的「统一安装」动作映射为 Flatpak 调用。"""
from __future__ import annotations

import shutil
import subprocess


class BackendError(RuntimeError):
    """后端不可用或执行失败。"""


class Backend:
    """封装 flatpak CLI。

    安全要点：
    - 所有命令以参数列表形式传递（不经过 shell），杜绝命令注入；
    - 每次调用前先检查 flatkap 是否可用，缺依赖时给出可读的提示而非异常堆栈。
    """

    def __init__(self, flatpak: str = "flatpak") -> None:
        self.flatpak = flatpak

    def available(self) -> bool:
        return shutil.which(self.flatpak) is not None

    def _run(self, args: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
        if not self.available():
            raise BackendError("未找到 flatpak，请先安装（https://flatpak.org/）。")
        return subprocess.run(
            [self.flatpak, *args], capture_output=capture, text=capture, check=False
        )

    def install(self, remote: str, ref: str, assume_yes: bool = False) -> int:
        args = ["install", remote, ref]
        if assume_yes:
            args.insert(1, "-y")
        return self._run(args).returncode

    def remove(self, ref: str, assume_yes: bool = False) -> int:
        args = ["uninstall", ref]
        if assume_yes:
            args.insert(1, "-y")
        return self._run(args).returncode

    def update(self, ref: str | None = None, assume_yes: bool = False) -> int:
        args = ["update"]
        if assume_yes:
            args.insert(1, "-y")
        if ref:
            args.append(ref)
        return self._run(args).returncode

    def list_installed(self) -> list[str]:
        proc = self._run(["list", "--app", "--columns=application"], capture=True)
        if proc.returncode != 0:
            return []
        return [line.strip() for line in proc.stdout.splitlines() if line.strip()]

    def is_installed(self, ref: str) -> bool:
        return ref in self.list_installed()