"""Lino 应用仓库索引的加载与查询。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Sequence

from .schema import App


class Registry:
    """读取 `index.json`，按 id 精确取用、按关键词模糊搜索。"""

    def __init__(self, apps: Iterable[App]) -> None:
        self._apps = {a.id: a for a in apps}

    @classmethod
    def load(cls, path: str | Path) -> "Registry":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"仓库索引不存在: {p}")
        raw = json.loads(p.read_text(encoding="utf-8"))
        return cls(App.from_dict(item) for item in raw.get("apps", []))

    def all(self) -> list[App]:
        return list(self._apps.values())

    def get(self, app_id: str) -> App:
        try:
            return self._apps[app_id]
        except KeyError as exc:
            raise LookupError(f"仓库中未找到应用: {app_id}") from exc

    def search(self, query: str) -> list[App]:
        q = query.casefold()
        return [
            a
            for a in self.all()
            if q in a.id.casefold() or q in a.name.casefold() or q in a.category.casefold()
        ]

    def by_ref(self, ref: str) -> App | None:
        return next((a for a in self.all() if a.ref == ref), None)