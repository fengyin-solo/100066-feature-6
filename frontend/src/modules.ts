/** 模块 key 与中文名的对照：与后端 app/registry.py 保持一致。
 *
 * 概览接口会返回 label，这里只作为接口不可用时的兜底，
 * 以及下钻页在数据返回前显示标题用。
 */
export const MODULE_LABELS: Record<string, string> = {
  sample: '样品受理',
  client: '委托单位',
  project: '检测项目',
  task: '检测任务',
  execute: '检测执行',
  result: '检测结果',
  review: '结果复核',
  instrument: '仪器设备',
  calibration: '校准记录',
  reagent: '试剂耗材',
  consume: '耗材领用',
  environment: '环境监控',
  report: '报告出具',
  issue: '报告变更',
  qc: '质量控制',
  complaint: '投诉处理',
  stockin: '样品流转',
  settlement: '检测结算',
}

export const MODULE_KEYS = Object.keys(MODULE_LABELS)

export function moduleLabel(key: string): string {
  return MODULE_LABELS[key] ?? key
}
