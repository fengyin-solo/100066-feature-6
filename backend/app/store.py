"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from typing import Any

from app.seed import SEED_ROWS


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        return sorted(self._tables)

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def module_summary(self, name: str) -> dict[str, int]:
        """单个模块的统计口径：总量、待处理量、异常量。

        概览卡片、模块行与下钻明细都从这里取数，保证三处看到的一直是同一份统计。
        """
        rows = self.rows(name)
        return {
            "created": len(rows),
            "pending": sum(1 for row in rows if row.get("pending")),
            "abnormal": sum(1 for row in rows if row.get("abnormal")),
        }

    def summary_for(self, names: list[str]) -> dict[str, int]:
        """多个模块的汇总统计，跨模块下钻（全部模块）时使用。"""
        total = {"created": 0, "pending": 0, "abnormal": 0}
        for name in names:
            part = self.module_summary(name)
            for key in total:
                total[key] += part[key]
        return total

    def filter_rows(
        self,
        name: str,
        *,
        kind: str = "all",
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """按下钻条件取模块记录：kind 限定待处理/异常，status 与列表页的状态筛选同口径。"""
        rows = self.rows(name)
        if kind == "pending":
            rows = [row for row in rows if row.get("pending")]
        elif kind == "abnormal":
            rows = [row for row in rows if row.get("abnormal")]
        if status:
            rows = [row for row in rows if row.get("status") == status]
        return [dict(row) for row in rows]

    def overview(self) -> dict[str, object]:
        modules: list[dict[str, object]] = []
        for name in self.module_names():
            modules.append({"name": name, **self.module_summary(name)})
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"cards": cards, "modules": modules}


store = Store()
