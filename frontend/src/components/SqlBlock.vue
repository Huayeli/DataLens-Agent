<template>
  <div class="sql-block">
    <button class="sql-head" @click="open = !open">
      <span class="label">SQL · 查询语句</span>
      <span class="chevron" :class="{ open }">❯</span>
    </button>
    <pre v-if="open" class="sql-body">{{ sql }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  sql: { type: String, default: '' },
})

const open = ref(false)
</script>

<style scoped>
.sql-block {
  border: 1px solid var(--border);
  border-radius: 4px;
  background: rgba(28,23,20,.6);
  overflow: hidden;
}
.sql-head {
  width: 100%;
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(201,169,98,.07);
  border: none;
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: .18em;
  text-transform: uppercase;
  padding: 10px 16px;
  cursor: pointer;
}
.sql-head:hover { background: rgba(201,169,98,.14); }
.chevron { transition: transform .25s ease; font-size: 12px; }
.chevron.open { transform: rotate(90deg); }
.sql-body {
  padding: 14px 16px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: var(--accent-bright);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>