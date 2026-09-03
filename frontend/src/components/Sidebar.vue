<template>
  <aside class="sidebar">

    <!-- 馆徽 -->
    <div class="logo-block">
      <div class="logo-mark">◈</div>
      <div>
        <div class="logo-name">数镜</div>
        <div class="logo-sub">DataLens · Ask Your Data</div>
      </div>
    </div>

    <div class="ornate-divider thin"></div>

    <!-- 导航 -->
    <nav class="nav">
      <div class="nav-label">导览</div>
      <router-link class="nav-item" to="/" exact-active-class="active">
        <span class="roman">I</span><span class="nav-text">探析</span><span class="nav-en">Analysis</span>
      </router-link>
      <router-link class="nav-item" to="/archives" active-class="active">
        <span class="roman">II</span><span class="nav-text">数据集</span><span class="nav-en">Datasets</span>
      </router-link>
      <router-link class="nav-item" to="/settings" active-class="active">
        <span class="roman">III</span><span class="nav-text">设置</span><span class="nav-en">Settings</span>
      </router-link>
    </nav>

    <!-- 上传 -->
    <button class="btn btn-brass upload-btn" :disabled="uploading" @click="selectFile">
      <span v-if="uploading">✒ 正在载入…</span>
      <span v-else>✒ 载入数据 · 开启探析</span>
    </button>
    <input ref="fileInput" type="file" accept=".csv" hidden @change="onFileChange" />

    <!-- 数据集列表 -->
    <div class="datasets">
      <div class="nav-label">全部数据集</div>
      <div v-if="!store.hasDatasets" class="datasets-empty">镜中尚无数据，请先载入</div>
      <button
        v-for="name in store.datasets"
        :key="name"
        class="dataset-item"
        :class="{ active: name === store.currentDataset }"
        @click="switchTo(name)"
      >
        <span class="ds-mark">❧</span>
        <span class="ds-name" :title="name">{{ name }}</span>
        <span v-if="name === store.currentDataset" class="ds-current">使用中</span>
      </button>
    </div>

    <div class="sidebar-foot">
      <span>数镜 Agent · v3.0</span>
      <span class="muted">Academia Style</span>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store'


const store = useAppStore()
const router = useRouter()
const fileInput = ref(null)
const uploading = ref(false)

function selectFile() {
  fileInput.value?.click()
}

async function onFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const result = await store.uploadFile(file)
    router.push('/')
  } catch (error) {
    alert(`Error: ${error.message}`)
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

async function switchTo(name) {
  await store.switchDataset(name)
  router.push('/')
}
</script>

<style scoped>
.sidebar {
  width: 300px;
  min-width: 300px;
  height: 100vh;
  background: linear-gradient(180deg, #211A16 0%, #1C1714 100%);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 28px 24px 18px;
  overflow-y: auto;
  position: relative;
  z-index: 100;
  transition: transform .3s ease;
}


.logo-block { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }

.logo-mark {
  width: 44px; height: 44px;
  border: 1.5px solid var(--accent);
  border-radius: 50%;
  display: grid; place-items: center;
  color: var(--accent);
  font-size: 20px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.15), 0 2px 8px rgba(0,0,0,.35);
}

.logo-name {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: .22em;
  font-size: 15px;
  font-weight: 600;
  color: var(--foreground);
}
.logo-sub {
  font-family: var(--font-display);
  letter-spacing: .18em;
  font-size: 9px;
  color: var(--accent);
  margin-top: 2px;
}

.nav { display: flex; flex-direction: column; gap: 4px; margin-top: 4px; }
.nav-label {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: .28em;
  font-size: 9px;
  color: var(--muted-foreground);
  margin: 18px 4px 8px;
}

.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 14px;
  border-radius: 4px;
  border: 1px solid transparent;
  color: var(--muted-foreground);
  text-decoration: none;
  transition: all .3s ease;
  position: relative;
}
.nav-item:hover { color: var(--foreground); background: rgba(201,169,98,.07); }
.nav-item.active {
  color: var(--accent);
  background: rgba(201,169,98,.1);
  border-color: rgba(201,169,98,.35);
}
.nav-item.active::before {
  content: ''; position: absolute; left: 0; top: 20%; bottom: 20%;
  width: 2px; background: var(--accent);
}
.nav-item .roman {
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--accent);
  opacity: .7;
  width: 16px;
}
.nav-text { font-family: var(--font-heading); font-size: 18px; font-weight: 500; }
.nav-en { margin-left: auto; font-size: 9px; letter-spacing: .12em; font-family: var(--font-display); opacity: .6; }

.upload-btn { width: 100%; margin: 18px 0 4px; }

.datasets { flex: 1; min-height: 0; overflow-y: auto; display: flex; flex-direction: column; }
.datasets-empty { color: var(--muted-foreground); font-size: 14px; padding: 6px 4px; font-style: italic; }

.dataset-item {
  display: flex; align-items: center; gap: 10px;
  width: 100%;
  padding: 10px 12px;
  margin-bottom: 6px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--foreground);
  font-family: var(--font-body);
  font-size: 15px;
  cursor: pointer;
  text-align: left;
  transition: all .3s ease;
}
.dataset-item:hover { border-color: rgba(201,169,98,.5); background: rgba(201,169,98,.06); }
.dataset-item.active {
  border-color: var(--accent);
  background: var(--brass-gradient);
  color: var(--on-brass);
}
.dataset-item.active .ds-mark { opacity: 1; }
.ds-mark { color: var(--accent); opacity: .7; font-size: 13px; }
.dataset-item.active .ds-mark { color: var(--on-brass); }
.ds-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ds-current {
  font-family: var(--font-display);
  font-size: 8px; letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--accent);
}
.dataset-item.active .ds-current { color: var(--on-brass); }

.sidebar-foot {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  display: flex; flex-direction: column;
  font-family: var(--font-display);
  font-size: 9px; letter-spacing: .16em;
  color: var(--muted-foreground);
}
</style>