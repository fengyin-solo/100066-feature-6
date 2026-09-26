"""模块注册表：概览看板与下钻视图共用的模块中文名与状态序列。

状态序列直接取各模块 service 里的 STATUS_ORDER，避免看板、下钻、列表三处各写一份口径。
按别名导入的原因见 app/routers/__init__.py：防止模块名撞内置类型。
"""
from __future__ import annotations

from app.services import sample as service_sample
from app.services import client as service_client
from app.services import project as service_project
from app.services import task as service_task
from app.services import execute as service_execute
from app.services import result as service_result
from app.services import review as service_review
from app.services import instrument as service_instrument
from app.services import calibration as service_calibration
from app.services import reagent as service_reagent
from app.services import consume as service_consume
from app.services import environment as service_environment
from app.services import report as service_report
from app.services import issue as service_issue
from app.services import qc as service_qc
from app.services import complaint as service_complaint
from app.services import stockin as service_stockin
from app.services import settlement as service_settlement

# 顺序与前端侧边导航保持一致，看板与下钻页都按这个顺序展示模块。
MODULE_LABELS: dict[str, str] = {
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

MODULE_STATUSES: dict[str, list[str]] = {
    service_sample.MODULE: service_sample.STATUS_ORDER,
    service_client.MODULE: service_client.STATUS_ORDER,
    service_project.MODULE: service_project.STATUS_ORDER,
    service_task.MODULE: service_task.STATUS_ORDER,
    service_execute.MODULE: service_execute.STATUS_ORDER,
    service_result.MODULE: service_result.STATUS_ORDER,
    service_review.MODULE: service_review.STATUS_ORDER,
    service_instrument.MODULE: service_instrument.STATUS_ORDER,
    service_calibration.MODULE: service_calibration.STATUS_ORDER,
    service_reagent.MODULE: service_reagent.STATUS_ORDER,
    service_consume.MODULE: service_consume.STATUS_ORDER,
    service_environment.MODULE: service_environment.STATUS_ORDER,
    service_report.MODULE: service_report.STATUS_ORDER,
    service_issue.MODULE: service_issue.STATUS_ORDER,
    service_qc.MODULE: service_qc.STATUS_ORDER,
    service_complaint.MODULE: service_complaint.STATUS_ORDER,
    service_stockin.MODULE: service_stockin.STATUS_ORDER,
    service_settlement.MODULE: service_settlement.STATUS_ORDER,
}


def module_label(key: str) -> str:
    """模块中文名；未知模块原样返回 key，不让看板因为新模块没登记而空白。"""
    return MODULE_LABELS.get(key, key)


def module_statuses(key: str) -> list[str]:
    """模块允许的状态序列；未知模块给空列表，下钻页据此隐藏状态筛选。"""
    return list(MODULE_STATUSES.get(key, []))
