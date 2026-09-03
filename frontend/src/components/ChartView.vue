<template>
  <div class="chart-wrap">
    <!-- 分类过多时的说明 -->
    <div v-if="total > LIMIT" class="chart-note">
      <span class="note-text">
        <span class="mark">✦</span>
        {{ showAll ? `已显示全部 ${total} 个分类` : `共 ${total} 个分类，为便于阅读默认仅展示前 ${LIMIT} 个` }}
      </span>
      <button class="note-btn" @click="toggleFull">
        {{ showAll ? '精简显示' : '查看全部分类' }}
      </button>
    </div>

    <div ref="el" class="chart"></div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { buildChartOption } from '@/utils/echarts'

// 分类超过该数量时默认精简展示
const LIMIT = 20

const props = defineProps({
  data: { type: Array, default: () => [] },
  type: { type: String, default: 'bar' },
  x: { type: String, default: '' },
  y: { type: String, default: '' },
})

const el = ref(null)
const showAll = ref(false)
let chart = null

const total = computed(() => props.data.length)

const displayData = computed(() => {
  if (!Array.isArray(props.data)) return []
  return showAll.value ? props.data : props.data.slice(0, LIMIT)
})

function render() {
  if (!chart) return
  const option = buildChartOption(displayData.value, props.type, props.x, props.y, {
    allowFull: showAll.value,
  })
  chart.setOption(option || {}, true)
}

function handleResize() {
  chart?.resize()
}

function toggleFull() {
  showAll.value = !showAll.value
}

onMounted(() => {
  chart = echarts.init(el.value, 'academia')
  render()
  window.addEventListener('resize', handleResize)
})

watch(() => [displayData.value, props.type, props.x, props.y], render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.chart-wrap { width: 100%; }
.chart { width: 100%; height: 320px; }

.chart-note {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--muted-foreground);
}
.note-text { display: inline-flex; align-items: center; gap: 6px; }
.mark { color: var(--accent); }

.note-btn {
  background: none;
  border: 1px solid rgba(201,169,98,.5);
  border-radius: 4px;
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
  padding: 4px 12px;
  cursor: pointer;
  transition: all .25s ease;
}
.note-btn:hover { background: var(--crimson); border-color: var(--crimson); color: var(--foreground); }
</style>