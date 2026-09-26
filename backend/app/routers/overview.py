"""运营概览与数据下钻接口：看板卡片、模块汇总、下钻明细共用 store 里的同一份统计。"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.registry import module_label, module_statuses
from app.store import store

router = APIRouter(prefix="/api/overview", tags=["运营概览"])

# 下钻范围：全部记录、待处理、异常；与概览卡片、模块行的三个数字一一对应。
DRILL_KINDS = ("all", "pending", "abnormal")
ALL_MODULES = "all"


@router.get("")
def overview() -> dict[str, object]:
    """运营概览：把各业务模块的待处理量汇总成看板卡片，并附上模块中文名。"""
    payload = store.overview()
    for item in payload["modules"]:  # type: ignore[union-attr]
        item["label"] = module_label(str(item["name"]))
    return payload


@router.get("/drilldown")
def drilldown(
    module: str = Query(default=ALL_MODULES, description="模块 key，all 表示跨模块汇总"),
    kind: str = Query(default="all", description="all、pending、abnormal"),
    status: str | None = Query(default=None, description="按状态二次筛选，口径与模块列表页一致"),
) -> dict[str, Any]:
    """下钻明细：返回某模块（或全部模块）在指定范围内的具体记录。

    记录数与概览数字天然一致——两边都走 store.module_summary / filter_rows 同一份统计；
    模块没有数据时返回空列表，由前端展示空态说明。
    """
    if kind not in DRILL_KINDS:
        raise HTTPException(status_code=400, detail=f"未知的下钻范围「{kind}」，可选：{ '、'.join(DRILL_KINDS) }")
    known = store.module_names()
    if module != ALL_MODULES and module not in known:
        raise HTTPException(status_code=404, detail=f"模块「{module}」不存在，请从运营概览重新进入")

    names = known if module == ALL_MODULES else [module]
    items: list[dict[str, Any]] = []
    for name in names:
        for row in store.filter_rows(name, kind=kind, status=status):
            # 跨模块时给每条记录补上所属模块，单模块保持原始字段，与列表页看到的列一致。
            items.append({"所属模块": module_label(name), **row} if module == ALL_MODULES else row)

    return {
        "module": module,
        "label": "全部模块" if module == ALL_MODULES else module_label(module),
        "kind": kind,
        "status": status,
        "statuses": [] if module == ALL_MODULES else module_statuses(module),
        "summary": store.summary_for(names),
        "total": len(items),
        "items": items,
    }
