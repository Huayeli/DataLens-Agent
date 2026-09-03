<template>
  <div class="data-table-wrap">
    <table v-if="keys.length" class="data-table">
      <thead>
        <tr>
          <th class="idx">#</th>
          <th v-for="key in keys" :key="key">{{ key }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="i">
          <td class="idx muted">{{ i + 1 }}</td>
          <td v-for="key in keys" :key="key" :class="{ num: isNumber(row[key]) }">{{ row[key] }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="table-empty">（当前没有可展示的行列数据）</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
})

const rows = computed(() => (Array.isArray(props.data) ? props.data : []))
const keys = computed(() => (rows.value.length ? Object.keys(rows.value[0]) : []))

function isNumber(value) {
  return typeof value === 'number' || (typeof value === 'string' && value.trim() !== '' && !Number.isNaN(Number(value)))
}
</script>

<style scoped>
.data-table-wrap {
  max-height: 420px;
  overflow: auto;
  border: 1px solid var(--border, rgba(255,255,255,.1));
  border-radius: 4px;
  background: rgba(0,0,0,.12);
}
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13.5px;
  line-height: 1.4;
}
.data-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #26211b;
  color: var(--accent, #C9A962);
  text-align: left;
  font-weight: 600;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border, rgba(255,255,255,.14));
  white-space: nowrap;
}
.data-table td {
  padding: 7px 12px;
  border-bottom: 1px solid rgba(255,255,255,.05);
  white-space: nowrap;
  max-width: 340px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table .idx { color: var(--muted-foreground, #9a8f83); text-align: right; }
.data-table .num { font-variant-numeric: tabular-nums; }
.table-empty {
  margin: 0;
  padding: 26px 16px;
  text-align: center;
  color: var(--muted-foreground, #9a8f83);
  font-size: 13px;
  font-style: italic;
}
</style>