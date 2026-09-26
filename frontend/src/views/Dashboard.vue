<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标，点击卡片或模块行可下钻到具体记录。</p>
      </div>
    </header>
    <div class="stat-row">
      <article
        v-for="card in cards"
        :key="card.label"
        class="stat-card clickable"
        @click="openCard(card)"
      >
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
      </article>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>业务模块</th><th>今日新增</th><th>待处理</th><th>异常量</th></tr>
      </thead>
      <tbody>
        <tr
          v-for="row in moduleRows"
          :key="row.name"
          class="clickable"
          @click="openModule(row, 'attention')"
        >
          <td>{{ row.label || row.name }}</td>
          <td>{{ row.created }}</td>
          <td>
            <button class="link" type="button" @click.stop="openModule(row, 'pending')">
              {{ row.pending }}
            </button>
          </td>
          <td>
            <button class="link" type="button" @click.stop="openModule(row, 'abnormal')">
              {{ row.abnormal }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchJson } from '@/api/client'

type Overview = {
  cards: { label: string; value: number }[]
  modules: { name: string; label: string; created: number; pending: number; abnormal: number }[]
}

// 卡片 → 下钻范围：待处理、异常量直达对应范围，其余看全部记录
const CARD_SCOPES: Record<string, string> = {
  业务模块: 'all',
  今日新增: 'all',
  待处理: 'pending',
  异常量: 'abnormal',
}

// 刷新后先渲染上次成功的快照，接口重试成功后再覆盖，卡片数值不会清零
const CACHE_KEY = 'overview-dashboard'

const FALLBACK: Overview = {
  cards: [{ label: '业务模块', value: 0 }, { label: '今日新增', value: 0 }, { label: '待处理', value: 0 }, { label: '异常量', value: 0 }],
  modules: [
    { name: 'sample', label: '样品受理', created: 0, pending: 0, abnormal: 0 },
    { name: 'client', label: '委托单位', created: 0, pending: 0, abnormal: 0 },
    { name: 'project', label: '检测项目', created: 0, pending: 0, abnormal: 0 },
    { name: 'task', label: '检测任务', created: 0, pending: 0, abnormal: 0 },
    { name: 'execute', label: '检测执行', created: 0, pending: 0, abnormal: 0 },
    { name: 'result', label: '检测结果', created: 0, pending: 0, abnormal: 0 },
    { name: 'review', label: '结果复核', created: 0, pending: 0, abnormal: 0 },
    { name: 'instrument', label: '仪器设备', created: 0, pending: 0, abnormal: 0 },
    { name: 'calibration', label: '校准记录', created: 0, pending: 0, abnormal: 0 },
    { name: 'reagent', label: '试剂耗材', created: 0, pending: 0, abnormal: 0 },
    { name: 'consume', label: '耗材领用', created: 0, pending: 0, abnormal: 0 },
    { name: 'environment', label: '环境监控', created: 0, pending: 0, abnormal: 0 },
    { name: 'report', label: '报告出具', created: 0, pending: 0, abnormal: 0 },
    { name: 'issue', label: '报告变更', created: 0, pending: 0, abnormal: 0 },
    { name: 'qc', label: '质量控制', created: 0, pending: 0, abnormal: 0 },
    { name: 'complaint', label: '投诉处理', created: 0, pending: 0, abnormal: 0 },
    { name: 'stockin', label: '样品流转', created: 0, pending: 0, abnormal: 0 },
    { name: 'settlement', label: '检测结算', created: 0, pending: 0, abnormal: 0 },
  ],
}

const router = useRouter()
const cards = ref<Overview['cards']>([])
const moduleRows = ref<Overview['modules']>([])

function applyPayload(payload: Overview) {
  cards.value = payload.cards
  moduleRows.value = payload.modules
}

function openCard(card: Overview['cards'][number]) {
  void router.push({
    path: '/overview/drilldown',
    query: { module: 'all', scope: CARD_SCOPES[card.label] ?? 'all' },
  })
}

function openModule(row: Overview['modules'][number], scope: string) {
  void router.push({ path: '/overview/drilldown', query: { module: row.name, scope } })
}

onMounted(async () => {
  const cached = sessionStorage.getItem(CACHE_KEY)
  if (cached) {
    try {
      applyPayload(JSON.parse(cached) as Overview)
    } catch {
      sessionStorage.removeItem(CACHE_KEY)
    }
  }
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    applyPayload(payload)
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(payload))
  } catch {
    if (!cached) {
      applyPayload(FALLBACK)
    }
  }
})
</script>
