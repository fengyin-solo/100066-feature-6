<template>
  <section class="page" data-module="drilldown">
    <header class="page-head">
      <div>
        <h2>{{ title }} · 数据下钻</h2>
        <p class="page-desc">与运营概览、模块列表共用同一份统计，切换条件只改变查看范围。</p>
      </div>
      <div class="page-actions">
        <RouterLink v-if="moduleKey !== 'all'" class="btn" :to="`/${moduleKey}`">前往{{ title }}列表</RouterLink>
        <button class="btn ghost" type="button" @click="backToOverview">返回运营概览</button>
      </div>
    </header>

    <div class="stat-row">
      <article
        v-for="tab in kindTabs"
        :key="tab.kind"
        class="stat-card clickable"
        :class="{ active: kind === tab.kind }"
        role="button"
        tabindex="0"
        @click="setKind(tab.kind)"
        @keydown.enter="setKind(tab.kind)"
      >
        <span class="stat-label">{{ tab.label }}</span>
        <strong class="stat-value">{{ tab.count }}</strong>
      </article>
    </div>

    <div v-if="statusOptions.length" class="filter-bar">
      <label class="filter-item">
        <span>当前状态</span>
        <select :value="status" @change="setStatus(($event.target as HTMLSelectElement).value)">
          <option value="">全部状态</option>
          <option v-for="item in statusOptions" :key="item" :value="item">{{ item }}</option>
        </select>
      </label>
    </div>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <template v-else-if="payload">
      <table v-if="payload.items.length" class="data-table">
        <thead>
          <tr>
            <th v-for="column in columns" :key="column">{{ column }}</th>
            <th>当前状态</th>
            <th>标记</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in payload.items" :key="`${row.id ?? index}-${row['所属模块'] ?? ''}`">
            <td v-for="column in columns" :key="column">{{ row[column] ?? '—' }}</td>
            <td>{{ row.status ?? '—' }}</td>
            <td>
              <span v-if="row.pending" class="tag pending">待处理</span>
              <span v-if="row.abnormal" class="tag abnormal">异常</span>
              <span v-if="!row.pending && !row.abnormal">—</span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-panel">
        <h3>当前条件下没有记录</h3>
        <p>{{ emptyHint }}</p>
        <button v-if="kind !== 'all' || status" class="btn" type="button" @click="resetConditions">
          查看全部记录
        </button>
      </div>
      <footer class="page-foot">
        <span>共 {{ payload.total }} 条记录 · 与运营概览同一份统计</span>
        <span>{{ conditionText }}</span>
      </footer>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchJson } from '@/api/client'
import { moduleLabel } from '@/modules'

type DrillKind = 'all' | 'pending' | 'abnormal'
type DrillRow = Record<string, string | number | boolean | null>
type DrillPayload = {
  module: string
  label: string
  kind: string
  status: string | null
  statuses: string[]
  summary: { created: number; pending: number; abnormal: number }
  total: number
  items: DrillRow[]
}

const KIND_LABELS: Record<DrillKind, string> = { all: '全部记录', pending: '待处理', abnormal: '异常量' }
// 行内字段里属于内部标记的 key，不作为业务列展示。
const INTERNAL_KEYS = new Set(['id', 'status', 'pending', 'abnormal'])

const route = useRoute()
const router = useRouter()

const payload = ref<DrillPayload | null>(null)
const errorMessage = ref('')

const moduleKey = computed(() => String(route.params.module || 'all'))
const kind = computed<DrillKind>(() => {
  const raw = route.query.kind
  return raw === 'pending' || raw === 'abnormal' ? raw : 'all'
})
const status = computed(() => (typeof route.query.status === 'string' ? route.query.status : ''))

const title = computed(() => payload.value?.label ?? (moduleKey.value === 'all' ? '全部模块' : moduleLabel(moduleKey.value)))
const statusOptions = computed(() => payload.value?.statuses ?? [])
const columns = computed(() => {
  const first = payload.value?.items[0]
  return first ? Object.keys(first).filter((key) => !INTERNAL_KEYS.has(key)) : []
})
const kindTabs = computed(() => {
  const summary = payload.value?.summary ?? { created: 0, pending: 0, abnormal: 0 }
  return [
    { kind: 'all' as DrillKind, label: KIND_LABELS.all, count: summary.created },
    { kind: 'pending' as DrillKind, label: KIND_LABELS.pending, count: summary.pending },
    { kind: 'abnormal' as DrillKind, label: KIND_LABELS.abnormal, count: summary.abnormal },
  ]
})
const conditionText = computed(() => {
  const parts = [KIND_LABELS[kind.value]]
  if (status.value) parts.push(`状态：${status.value}`)
  return `当前条件：${parts.join(' · ')}`
})
const emptyHint = computed(() => {
  if (!payload.value) return ''
  if (payload.value.summary.created === 0) {
    return `「${title.value}」还没有任何记录，可先到模块列表页登记，登记后概览与这里会同步更新。`
  }
  return `「${title.value}」在${conditionText.value.replace('当前条件：', '')}下没有匹配记录，可切换条件或查看全部。`
})

function setKind(next: DrillKind) {
  void router.replace({ query: { ...route.query, kind: next === 'all' ? undefined : next } })
}

function setStatus(next: string) {
  void router.replace({ query: { ...route.query, status: next || undefined } })
}

function resetConditions() {
  void router.replace({ query: {} })
}

function backToOverview() {
  void router.push('/')
}

async function reload() {
  errorMessage.value = ''
  const query = new URLSearchParams({ module: moduleKey.value, kind: kind.value })
  if (status.value) query.set('status', status.value)
  try {
    payload.value = await fetchJson<DrillPayload>(`/api/overview/drilldown?${query.toString()}`)
  } catch (error) {
    payload.value = null
    errorMessage.value = error instanceof Error ? error.message : '下钻数据读取失败'
  }
}

watch([moduleKey, kind, status], reload, { immediate: true })
</script>
