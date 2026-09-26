"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from typing import Any

from app.seed import SEED_ROWS

MODULE_LABELS = {
    "sample": "样品受理",
    "client": "委托单位",
    "project": "检测项目",
    "task": "检测任务",
    "execute": "检测执行",
    "result": "检测结果",
    "review": "结果复核",
    "instrument": "仪器设备",
    "calibration": "校准记录",
    "reagent": "试剂耗材",
    "consume": "耗材领用",
    "environment": "环境监控",
    "report": "报告出具",
    "issue": "报告变更",
    "qc": "质量控制",
    "complaint": "投诉处理",
    "stockin": "样品流转",
    "settlement": "检测结算",
}

# 下钻范围：all 全部、pending 待处理、abnormal 异常、attention 待处理与异常
DRILLDOWN_SCOPES = ("all", "pending", "abnormal", "attention")


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        return sorted(self._tables)

    def module_label(self, module: str) -> str:
        return MODULE_LABELS.get(module, module)

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def module_stats(self, module: str) -> dict[str, object]:
        """单个模块的统计口径：概览卡片、下钻明细都从这里取数，保证三处一致。"""
        rows = self.rows(module)
        return {
            "name": module,
            "label": self.module_label(module),
            "created": len(rows),
            "pending": sum(1 for row in rows if row.get("pending")),
            "abnormal": sum(1 for row in rows if row.get("abnormal")),
        }

    def overview(self) -> dict[str, object]:
        modules = [self.module_stats(name) for name in self.module_names()]
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"cards": cards, "modules": modules}

    def drilldown(
        self,
        module: str,
        *,
        scope: str = "all",
        status: str | None = None,
    ) -> dict[str, object] | None:
        """概览下钻：按模块与范围列出具体记录，状态过滤与列表页口径一致。

        module 传 "all" 时跨模块汇总；模块不存在时返回 None 交给接口层报 404。
        """
        if module == "all":
            names = self.module_names()
        elif module in self._tables:
            names = [module]
        else:
            return None

        def in_scope(row: dict[str, Any]) -> bool:
            if scope == "pending":
                return bool(row.get("pending"))
            if scope == "abnormal":
                return bool(row.get("abnormal"))
            if scope == "attention":
                return bool(row.get("pending")) or bool(row.get("abnormal"))
            return True

        items: list[dict[str, Any]] = []
        statuses: list[str] = []
        for name in names:
            for row in self.rows(name):
                if not in_scope(row):
                    continue
                current = str(row.get("status") or "")
                if current and current not in statuses:
                    statuses.append(current)
                if status and row.get("status") != status:
                    continue
                items.append({**row, "module": name, "module_label": self.module_label(name)})

        stats_list = [self.module_stats(name) for name in names]
        stats = {
            "created": sum(int(item["created"]) for item in stats_list),
            "pending": sum(int(item["pending"]) for item in stats_list),
            "abnormal": sum(int(item["abnormal"]) for item in stats_list),
        }
        return {
            "module": module,
            "label": "全部模块" if module == "all" else self.module_label(module),
            "scope": scope,
            "status": status,
            "statuses": statuses,
            "stats": stats,
            "total": len(items),
            "items": items,
        }


store = Store()
