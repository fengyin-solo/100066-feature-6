"""实验室样品检测平台 后端服务入口。

启动：uvicorn app.main:app --host 127.0.0.1 --port 8000
健康检查：GET /api/health
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import ROUTERS
from app.store import DRILLDOWN_SCOPES, store

app = FastAPI(title="实验室样品检测平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in ROUTERS:
    app.include_router(module.router)


@app.get("/api/health")
def health() -> dict[str, object]:
    """健康检查：确认服务已经监听、示例数据已经就绪。"""
    return {"ok": True, "app": settings.app_name, "modules": len(store.module_names())}


@app.get("/api/overview")
def overview() -> dict[str, object]:
    """运营概览：把各业务模块的待处理量汇总成看板卡片。"""
    return store.overview()


@app.get("/api/overview/drilldown")
def overview_drilldown(
    module: str = Query(default="all", description="模块键名，all 表示跨模块汇总"),
    scope: str = Query(default="all", description="all、pending、abnormal、attention"),
    status: str | None = Query(default=None, description="按当前状态二次过滤，口径与列表页一致"),
) -> dict[str, object]:
    """概览下钻：与 /api/overview 同一份统计，列出数字背后的具体记录。"""
    if scope not in DRILLDOWN_SCOPES:
        raise HTTPException(
            status_code=400,
            detail=f"下钻范围「{scope}」不支持，可选：{'、'.join(DRILLDOWN_SCOPES)}",
        )
    payload = store.drilldown(module, scope=scope, status=status)
    if payload is None:
        raise HTTPException(status_code=404, detail=f"业务模块「{module}」不存在")
    return payload
