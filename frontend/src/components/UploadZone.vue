<template>
  <div
    class="upload-zone ornate-frame"
    :class="{ dragging }"
    @click="pick"
    @dragover.prevent="dragging = true"
    @dragleave.prevent="dragging = false"
    @drop.prevent="drop"
  >
    <input ref="input" type="file" accept=".csv" hidden @change="onChange" />

    <template v-if="!uploading">
      <div class="mark">⚜</div>
      <div class="title">载入一份新的数据集</div>
      <div class="hint">拖入 CSV 文件，或点击此处选择文件</div>
      <div class="hint small muted">支持 UTF-8 / GBK 编码 · 自动清洗并建表</div>
    </template>
    <template v-else>
      <div class="mark thinking-ornament">✒</div>
      <div class="title">正在导入数据…</div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['uploaded', 'error'])
const input = ref(null)
const uploading = ref(false)
const dragging = ref(false)

function pick() {
  if (!uploading.value) input.value?.click()
}

function onChange(event) {
  const file = event.target.files?.[0]
  if (file) upload(file)
  event.target.value = ''
}

function drop(event) {
  dragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) upload(file)
}

async function upload(file) {
  if (!file.name.toLowerCase().endsWith('.csv')) {
    emit('error', '仅支持 CSV 文件')
    return
  }
  uploading.value = true
  try {
    emit('uploaded', file)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-zone {
  border: 1px solid var(--border);
  border-style: dashed;
  border-radius: 4px;
  background: rgba(37,30,25,.55);
  text-align: center;
  padding: 44px 24px;
  cursor: pointer;
  transition: all .3s ease;
}
.upload-zone:hover { border-color: var(--accent); background: rgba(201,169,98,.06); }
.upload-zone.dragging {
  border-color: var(--accent);
  background: rgba(201,169,98,.1);
  box-shadow: var(--brass-glow);
}
.mark {
  font-size: 34px;
  color: var(--accent);
  margin-bottom: 10px;
  line-height: 1;
}
.thinking-ornament { animation: pulse-brass 1.1s ease-in-out infinite; }
@keyframes pulse-brass {
  0%, 100% { opacity: .4; transform: scale(.92); }
  50% { opacity: 1; transform: scale(1.06); }
}
.title {
  font-family: var(--font-heading);
  font-size: 22px;
  margin-bottom: 6px;
}
.hint { color: var(--foreground); opacity: .85; font-size: 15px; }
.hint.small { font-size: 13px; margin-top: 4px; }
</style>