"""威胁签名数据库：加载与查询。"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Signature:
    algo: str  # "sha256" | "md5"
    value: str  # 小写十六进制
    name: str


class ThreatDB:
    """按 (算法, 哈希值) 索引签名；后续可扩展 ClamAV .hdb / .ldb 与在线威胁情报。"""

    def __init__(self, signatures: list[Signature]) -> None:
        self._index = {(s.algo, s.value.casefold()): s for s in signatures}

    @classmethod
    def load(cls, path: str | Path) -> "ThreatDB":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        sigs: list[Signature] = []
        for item in raw.get("signatures", []):
            name = str(item.get("name", "未命名威胁"))
            for algo in ("sha256", "md5"):
                value = item.get(algo)
                if value:
                    sigs.append(Signature(algo, str(value).casefold(), name))
        return cls(sigs)

    def lookup(self, algo: str, value: str) -> Signature | None:
        return self._index.get((algo, value.casefold()))