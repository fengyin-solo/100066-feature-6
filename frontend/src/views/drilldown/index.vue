<template>
  <section class="page" data-module="drilldown">
    <header class="page-head">
      <div>
        <h2>概览下钻 · {{ payload?.label ?? '…' }}</h2>
        <p class="page-desc">与运营概览同一份统计，切换条件查看数字背后的具体记录。</p>
      </div>
      <div class="page-actions">
        <button v-if="moduleKey !== 'all'" class="btn" type="button" @click="goModuleList">前往模块列表</button>
        <button class="btn ghost" type="button" @click="backToOverview">返回概览</button>
      </div>
    </header>

    <div class="stat-row">
      <article v-for="item in statCards" :key="item.label" class="stat-card">
        <span class="stat-label">{{ item.label }}</span>
        <strong class="stat-value">{{ item.value }}</strong>
      </article>
    </div>

    <div class="filter-bar">
      <div class="scope-tabs">
        <button
          v-for="item in SCOPES"
          :key="item.key"
          class="btn scope-tab"
          :class="{ active: item.key === scopeKey }"
          type="button"
          @click="switchScope(item.key)"
        >
          {{ item.label }}
        </button>
      </div>
      <label class="filter-item">
        <span>当前状态</span>
        <select :value="statusKey" @change="onStatusChange">
          <option value="">全部状态</option>
          <option v-for="item in payload?.statuses ?? []" :key="item" :value="item">{{ item }}</option>
        </select>
      </label>
    </div>

    <table v-if="moduleKey === 'all'" class="data-table">
      <thead>
        <tr><th>业务模块</th><th>记录</th><th>当前状态</th><th>待处理</th><th>异常</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in items" :key="`${row.module}-${row.id}`">
          <td>
            <button class="link" type="button" @click="openModule(String(row.module))">
              {{ row.module_label }}
            </button>
          </td>
          <td>{{ rowTitle(row) }}</td>
          <td>{{ row.status ?? '—' }}</td>
          <td>{{ row.pending ? '是' : '—' }}</td>
          <td>{{ row.abnormal ? '是' : '—' }}</td>
        </tr>
        <tr v-if="!items.length">
          <td colspan="5" class="empty-state">{{ emptyText }}</td>
        </tr>
      </tbody>
    </table>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th v-for="column in bizColumns" :key="column">{{ column }}</th>
          <th>当前状态</th><th>待处理</th><th>异常</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in items" :key="String(row.id)">
          <td v-for="column in bizColumns" :key="column">{{ row[column] ?? '—' }}</td>
          <td>{{ row.status ?? '—' }}</td>
          <td>{{ row.pending ? '是' : '—' }}</td>
          <td>{{ row.abnormal ? '是' : '—' }}</td>
        </tr>
        <tr v-if="!items.length">
          <td :colspan="bizColumns.length + 3" class="empty-state">{{ emptyText }}</td>
        </tr>
      </tbody>
    </table>

    <footer class="page-foot">
      <span>共 {{ payload?.total ?? 0 }} 条记录</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { request } from '@/api/client'

type DrillItem = Record<string, string | number | boolean | null | undefined>

type Drilldown = {
  module: string
  label: string
  scope: string
  status: string | null
  statuses: string[]
  stats: { created: number; pending: number; abnormal: number }
  total: number
  items: DrillItem[]
}

const SCOPES = [
  { key: 'all', label: '全部记录' },
  { key: 'pending', label: '待处理' },
  { key: 'abnormal', label: '异常' },
  { key: 'attention', label: '待处理与异常' },
]

// 内部字段不参与业务列展示，与模块列表页保持同一套业务字段口径
const INTERNAL_KEYS = ['id', 'status', 'pending', 'abnormal', 'module', 'module_label']

const route = useRoute()
const router = useRouter()

const payload = ref<Drilldown | null>(null)
const errorMessage = ref('')

const moduleKey = computed(() => String(route.query.module || 'all'))
const scopeKey = computed(() => String(route.query.scope || 'all'))
const statusKey = computed(() => (route.query.status ? String(route.query.status) : ''))

const items = computed(() => payload.value?.items ?? [])

const statCards = computed(() => {
  const stats = payload.value?.stats ?? { created: 0, pending: 0, abnormal: 0 }
  return [
    { label: '今日新增', value: stats.created },
    { label: '待处理', value: stats.pending },
    { label: '异常量', value: stats.abnormal },
    { label: '当前结果', value: payload.value?.total ?? 0 },
  ]
})

const bizColumns = computed(() => {
  const first = items.value[0]
  if (!first) return []
  return Object.keys(first).filter((key) => !INTERNAL_KEYS.includes(key))
})

const emptyText = computed(() => {
  const data = payload.value
  if (!data) return '数据加载中…'
  if (data.stats.created === 0) {
    return moduleKey.value === 'all'
      ? '各业务模块暂无数据，可先到模块列表页登记'
      : `「${data.label}」模块暂无数据，可先到模块列表页登记`
  }
  const scopeLabel = SCOPES.find((item) => item.key === scopeKey.value)?.label ?? ''
  const statusPart = statusKey.value ? `，状态「${statusKey.value}」` : ''
  return `「${data.label}」在「${scopeLabel}」条件下暂无记录${statusPart}，可切换条件或返回概览`
})

function rowTitle(row: DrillItem) {
  const key = Object.keys(row).find((name) => !INTERNAL_KEYS.includes(name))
  return key ? row[key] : `#${String(row.id ?? '')}`
}

function switchScope(next: string) {
  // 切换主条件时重置状态二次过滤，避免残留上一个范围里的状态值
  void router.replace({ query: { module: moduleKey.value, scope: next } })
}

function onStatusChange(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  void router.replace({
    query: { module: moduleKey.value, scope: scopeKey.value, status: value || undefined },
  })
}

function openModule(module: string) {
  void router.push({ path: '/overview/drilldown', query: { module, scope: scopeKey.value } })
}

function goModuleList() {
  void router.push(`/${moduleKey.value}`)
}

function backToOverview() {
  void router.push('/')
}

async function reload() {
  errorMessage.value = ''
  const query = new URLSearchParams({ module: moduleKey.value, scope: scopeKey.value })
  if (statusKey.value) query.set('status', statusKey.value)
  try {
    const response = await request(`/api/overview/drilldown?${query.toString()}`)
    if (!response.ok) {
      let detail = `接口返回 ${response.status}，数据未更新`
      try {
        const body = (await response.json()) as { detail?: string }
        if (body.detail) detail = body.detail
      } catch {
        // 保留默认错误说明
      }
      throw new Error(detail)
    }
    payload.value = (await response.json()) as Drilldown
  } catch (error) {
    payload.value = null
    errorMessage.value = error instanceof Error ? error.message : '下钻数据读取失败'
  }
}

watch([moduleKey, scopeKey, statusKey], () => void reload(), { immediate: true })
</script>
