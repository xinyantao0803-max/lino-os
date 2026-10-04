"""扫描引擎：对字节/文件做哈希匹配并给出判定。"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .db import ThreatDB

# EICAR：杀毒行业标准的合法测试样本（无真实危害），用于验证扫描链路。
EICAR = r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*".encode("ascii")


@dataclass(frozen=True)
class Verdict:
    malicious: bool
    hit_name: str | None = None
    hash: str | None = None


def _digests(data: bytes) -> dict[str, str]:
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


class Scanner:
    def __init__(self, db: ThreatDB) -> None:
        self.db = db

    def scan_bytes(self, data: bytes) -> Verdict:
        for algo, digest in _digests(data).items():
            sig = self.db.lookup(algo, digest)
            if sig:
                return Verdict(malicious=True, hit_name=sig.name, hash=digest)
        return Verdict(malicious=False)

    def scan_file(self, path: str | Path) -> Verdict:
        return self.scan_bytes(Path(path).read_bytes())

    def selftest(self) -> bool:
        return self.scan_bytes(EICAR).malicious