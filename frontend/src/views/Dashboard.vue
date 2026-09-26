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
        role="button"
        tabindex="0"
        @click="drillCard(card.label)"
        @keydown.enter="drillCard(card.label)"
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
        <tr v-for="row in moduleRows" :key="row.name">
          <td>
            <RouterLink class="link" :to="drillTo(row.name, 'all')">{{ row.label ?? row.name }}</RouterLink>
          </td>
          <td>
            <RouterLink class="link" :to="drillTo(row.name, 'all')">{{ row.created }}</RouterLink>
          </td>
          <td>
            <RouterLink class="link" :to="drillTo(row.name, 'pending')">{{ row.pending }}</RouterLink>
          </td>
          <td>
            <RouterLink class="link" :to="drillTo(row.name, 'abnormal')">{{ row.abnormal }}</RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter, type RouteLocationRaw } from 'vue-router'

import { fetchJson } from '@/api/client'
import { MODULE_KEYS, moduleLabel } from '@/modules'

type DrillKind = 'all' | 'pending' | 'abnormal'

type Overview = {
  cards: { label: string; value: number }[]
  modules: { name: string; label?: string; created: number; pending: number; abnormal: number }[]
}

const CACHE_KEY = 'lab-overview-cache'

const router = useRouter()
const cards = ref<Overview['cards']>([])
const moduleRows = ref<Overview['modules']>([])

// 卡片文案与下钻范围的对应关系：待处理、异常量精确下钻，其余看全部记录。
const CARD_KINDS: Record<string, DrillKind> = { 待处理: 'pending', 异常量: 'abnormal' }

function drillTo(module: string, kind: DrillKind): RouteLocationRaw {
  return {
    name: 'overview-drilldown',
    params: { module },
    query: kind === 'all' ? {} : { kind },
  }
}

function drillCard(label: string) {
  void router.push(drillTo('all', CARD_KINDS[label] ?? 'all'))
}

function apply(payload: Overview) {
  cards.value = payload.cards
  moduleRows.value = payload.modules
}

onMounted(async () => {
  // 先恢复上次成功的看板数据，刷新页面时卡片数值不丢；接口返回后再覆盖并更新缓存。
  let hydrated = false
  try {
    const cached = window.localStorage.getItem(CACHE_KEY)
    if (cached) {
      apply(JSON.parse(cached) as Overview)
      hydrated = true
    }
  } catch {
    window.localStorage.removeItem(CACHE_KEY)
  }
  try {
    const payload = await fetchJson<Overview>('/api/overview')
    apply(payload)
    window.localStorage.setItem(CACHE_KEY, JSON.stringify(payload))
  } catch {
    if (!hydrated) {
      cards.value = [
        { label: '业务模块', value: 0 },
        { label: '今日新增', value: 0 },
        { label: '待处理', value: 0 },
        { label: '异常量', value: 0 },
      ]
      moduleRows.value = MODULE_KEYS.map((name) => ({
        name,
        label: moduleLabel(name),
        created: 0,
        pending: 0,
        abnormal: 0,
      }))
    }
  }
})
</script>
