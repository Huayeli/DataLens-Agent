<template>
  <div class="view">
    <header class="page-head">
      <div class="display-label">II · Datasets</div>
      <div class="title-line">
        <h1>数据集 <span class="brass">· 数据管理</span></h1>
        <span class="badge"><span class="dot"></span>共 {{ store.datasets.length }} 卷</span>
      </div>
      <p class="sub">数据集的载入、查看与清理。就绪后即可前往「探析」展开分析。</p>
    </header>

    <UploadZone @uploaded="onUploaded" @error="onError" />

    <div v-if="store.hasDatasets" class="datasets-section">
      <div class="ornate-divider thin"></div>
      <div class="section-title">全部数据集</div>

      <div v-for="name in store.datasets" :key="name" class="archive-row panel panel-hover">
        <div class="row-main">
          <span class="row-mark">❧</span>
          <div class="row-info">
            <div class="row-name">{{ name }}</div>
            <div class="row-meta muted">{{ metaText(name) }}</div>
          </div>
          <span v-if="name === store.currentDataset" class="badge current-badge">使用中</span>
        </div>
        <div class="row-actions">
          <button class="btn btn-outline" @click="preview(name)">查看</button>
          <button
            v-if="confirmName !== name"
            class="btn btn-danger"
            @click="confirmName = name"
          >销毁</button>
          <template v-else>
            <button class="btn btn-danger" @click="remove(name)">确认销毁</button>
            <button class="btn btn-ghost" @click="confirmName = ''">取消</button>
          </template>
        </div>
      </div>
    </div>

    <!-- 预览面板 -->
    <div v-if="stats" class="preview-panel panel ornate-frame">
      <div class="preview-head">
        <div>
          <div class="display-label">Excerpt</div>
          <h2 class="preview-title">{{ stats.name }}</h2>
        </div>
        <button class="btn btn-ghost" @click="stats = null">关闭 ✕</button>
      </div>
      <p class="muted" style="margin-bottom:14px;">
        共 <span class="brass">{{ stats.rows }}</span> 行 · {{ stats.columns.length }} 列
        <span v-if="previewLoading">（正在读取…）</span>
      </p>
      <div v-if="previewLoading" class="thinking">
        <span class="ornament">✒</span><span>正在读取预览</span><span class="dots"></span>
      </div>
      <DataTable v-else-if="previewData.length" :data="previewData" />
      <p v-else class="muted">暂无数据</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-banner">Error: {{ errorMsg }}</div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAppStore } from '@/store'
import { api } from '@/api'
import UploadZone from '@/components/UploadZone.vue'
import DataTable from '@/components/DataTable.vue'

const store = useAppStore()
const stats = ref(null)
const previewData = ref([])
const previewLoading = ref(false)
const confirmName = ref('')
const errorMsg = ref('')

const statCache = new Map()

onMounted(() => {
  store.loadDatasets().catch(() => {})
})

function metaText(name) {
  const info = statCache.get(name)
  if (!info) return '点击「查看」获取统计'
  return `${info.rows} 行 · ${info.columns.length} 列 · ${info.columns.map((c) => c.name).join(' / ')}`
}

async function onUploaded(file) {
  errorMsg.value = ''
  try {
    const result = await store.uploadFile(file)
    statCache.delete(result.table)
    await preview(result.table)
  } catch (error) {
    errorMsg.value = error.message
  }
}

function onError(msg) {
  errorMsg.value = msg
}

async function preview(name) {
  errorMsg.value = ''
  stats.value = null
  previewLoading.value = true
  try {
    const info = await api.datasetStats(name)
    if (!info.success) throw new Error(info.msg || '无法读取统计')
    statCache.set(name, info)
    stats.value = info
    const data = await api.datasetData(name)
    previewData.value = data.data || []
  } catch (error) {
    errorMsg.value = error.message
    previewData.value = []
  } finally {
    previewLoading.value = false
  }
}

async function remove(name) {
  errorMsg.value = ''
  try {
    const result = await api.deleteDataset(name)
    if (!result.success) throw new Error(result.msg || '删除失败')
    statCache.delete(name)
    if (stats.value?.name === name) stats.value = null
    confirmName.value = ''
    await store.loadDatasets()
  } catch (error) {
    errorMsg.value = error.message
  }
}
</script>

<style scoped>
.datasets-section { margin-top: 8px; }
.section-title {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: .28em;
  font-size: 10px;
  color: var(--accent);
  margin: 4px 0 14px;
}

.archive-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.row-main { display: flex; align-items: center; gap: 14px; min-width: 0; }
.row-mark { color: var(--accent); font-size: 16px; opacity: .8; }
.row-name { font-family: var(--font-heading); font-size: 20px; }
.row-meta { font-size: 13px; margin-top: 2px; }
.current-badge { flex-shrink: 0; }
.row-actions { display: flex; gap: 10px; align-items: center; }

.preview-panel { padding: 24px 26px; margin-top: 24px; }
.preview-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 10px;
}
.preview-title { font-size: 26px; margin-top: 4px; }

.error-banner {
  margin-top: 18px;
  border: 1px solid rgba(139,38,53,.7);
  background: rgba(139,38,53,.12);
  color: #D98A8A;
  border-radius: 4px;
  padding: 12px 16px;
  font-size: 14px;
}
</style>