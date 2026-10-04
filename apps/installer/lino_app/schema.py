"""Lino 应用清单数据模型与校验。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REQUIRED_FIELDS = ("id", "name", "category", "summary", "backend", "remote", "ref")


@dataclass(frozen=True)
class App:
    """一条 Lino 应用仓库索引中的应用清单。

    field: backend 标识后端类型（`flatpak` / `waydroid` / `qemu`），
    当前仅实现 flatpak，其余为规划中的后端。
    """

    id: str
    name: str
    category: str
    summary: str
    backend: str
    remote: str
    ref: str
    description: str = ""
    permissions: tuple[str, ...] = ()
    recommended: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "App":
        missing = [k for k in REQUIRED_FIELDS if not str(data.get(k, "")).strip()]
        if missing:
            raise ValueError(f"应用清单缺少必填字段: {', '.join(missing)}")
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            summary=data["summary"],
            backend=data["backend"],
            remote=data["remote"],
            ref=data["ref"],
            description=str(data.get("description", "")),
            permissions=tuple(data.get("permissions", [])),
            recommended=bool(data.get("recommended", False)),
        )