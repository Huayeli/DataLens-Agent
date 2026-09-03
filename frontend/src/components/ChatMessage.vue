<template>
  <div class="message" :class="message.role">
    <!-- 用户 -->
    <div v-if="message.role === 'user'" class="bubble user-bubble">{{ message.content }}</div>

    <!-- AI -->
    <div v-else class="bubble ai-bubble" :class="{ error: message.error }">
      <div class="ai-mark">❧</div>
      <div class="ai-content">
        <template v-if="!message.error">
          <p
            v-for="(para, i) in paragraphs"
            :key="i"
            class="ai-para"
            :class="{ 'drop-cap': i === 0 && paragraphs.length > 1 }"
          >{{ para }}</p>
          <p v-if="!paragraphs.length" class="ai-para muted">（无文字回答）</p>
        </template>
        <p v-else class="ai-para error-text">{{ message.content }}</p>

        <!-- 分析结果 -->
        <template v-if="hasResult">
          <!-- 图表型结果：图表 / 明细 两个页签切换 -->
          <template v-if="message.chart !== 'table'">
            <div class="result-tabs">
              <button
                class="tab"
                :class="{ active: tab === 'chart' }"
                @click="tab = 'chart'"
              >图表</button>
              <button
                class="tab"
                :class="{ active: tab === 'table' }"
                @click="tab = 'table'"
              >明细</button>
            </div>

            <!-- 图表 -->
            <div v-if="tab === 'chart'" class="result-body">
              <ChartView
                :data="message.data"
                :type="message.chart"
                :x="message.x"
                :y="message.y"
              />
            </div>

            <!-- 明细：本次 SQL 返回的行 -->
            <div v-else class="result-body">
              <div class="body-note">
                <span class="mark">✧</span>
                本次查询返回 {{ message.data.length }} 行（用于生成上方图表）
              </div>
              <DataTable :data="message.data" />
            </div>
          </template>

          <!-- 表格型结果：直接展示明细表格 -->
          <div v-else class="result-body">
            <div class="body-note">
              <span class="mark">✧</span>
              本次查询返回 {{ message.data.length }} 行
            </div>
            <DataTable :data="message.data" />
          </div>
        </template>

        <SqlBlock v-if="message.sql" class="sql" :sql="message.sql" />

        <!-- 查看数据集原始记录 -->
        <div v-if="rawDataset" class="raw-bar">
          <button class="raw-btn" :disabled="rawLoading" @click="toggleRaw">
            {{ rawOpen ? '收起原始数据' : '查看原始数据' }}
          </button>
          <span class="raw-hint">
            展示数据集「{{ rawDataset }}」的原始行列，最多前 200 行
          </span>
        </div>

        <div v-if="rawOpen" class="result-body raw-body">
          <div v-if="rawLoading" class="thinking">
            <span class="ornament">✒</span>
            <span>正在读取原始数据</span><span class="dots"></span>
          </div>
          <DataTable v-else-if="rawRows.length" :data="rawRows" />
          <p v-else-if="rawError" class="raw-error">Error: {{ rawError }}</p>
          <p v-else class="muted">原始数据为空</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAppStore } from '@/store'
import { api } from '@/api'
import ChartView from '@/components/ChartView.vue'
import DataTable from '@/components/DataTable.vue'
import SqlBlock from '@/components/SqlBlock.vue'

const props = defineProps({
  message: { type: Object, required: true },
})

const store = useAppStore()

const paragraphs = computed(() =>
  (props.message.content || '').split(/\n+/).map((p) => p.trim()).filter(Boolean)
)

const hasResult = computed(() => Array.isArray(props.message.data) && props.message.data.length > 0)

// 该回答对应的数据集（优先使用回答当时的数据集）
const rawDataset = computed(() => props.message.dataset || store.currentDataset || '')

// 图表型回答默认展示图表页签
const tab = ref('chart')

const rawOpen = ref(false)
const rawLoading = ref(false)
const rawRows = ref([])
const rawError = ref('')

async function toggleRaw() {
  rawOpen.value = !rawOpen.value
  if (!rawOpen.value || rawRows.value.length) return
  rawLoading.value = true
  rawError.value = ''
  try {
    const data = await api.datasetData(rawDataset.value)
    rawRows.value = data.data || []
  } catch (error) {
    rawError.value = error.message
  } finally {
    rawLoading.value = false
  }
}
</script>

<style scoped>
.message { display: flex; margin-bottom: 22px; }
.message.user { justify-content: flex-end; }

.bubble { max-width: 86%; }

.user-bubble {
  background: var(--brass-gradient);
  color: var(--on-brass);
  text-shadow: var(--engraved);
  padding: 12px 20px;
  border-radius: 4px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 2px 8px rgba(0,0,0,.3);
  font-size: 16px;
  line-height: 1.55;
}

.ai-bubble {
  display: flex; gap: 14px;
  background: var(--background-alt);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 18px 20px;
  min-width: 0;
}
.ai-bubble.error { border-color: rgba(139,38,53,.7); }

.ai-mark {
  color: var(--accent);
  font-size: 18px;
  line-height: 1.4;
  flex-shrink: 0;
  opacity: .85;
}

.ai-content { min-width: 0; flex: 1; }
.ai-para { margin-bottom: 10px; font-size: 16.5px; }
.ai-para:last-child { margin-bottom: 0; }
.error-text { color: #D98A8A; }

.result-tabs {
  display: flex; align-items: center; gap: 8px;
  margin: 18px 0 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.result-tabs .hint { font-size: 12px; color: var(--muted-foreground); margin-left: 6px; }

.tab {
  background: none;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--muted-foreground);
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: .18em;
  text-transform: uppercase;
  padding: 6px 16px;
  cursor: pointer;
  transition: all .25s ease;
}
.tab:hover { color: var(--accent); border-color: var(--accent); }
.tab.active {
  background: var(--brass-gradient);
  color: var(--on-brass);
  border-color: transparent;
  text-shadow: var(--engraved);
}

.result-body {
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 14px;
  background: rgba(28,23,20,.35);
  min-width: 0;
}

.body-note {
  font-size: 12px;
  color: var(--muted-foreground);
  margin-bottom: 10px;
}
.body-note .mark { color: var(--accent); margin-right: 6px; }

.sql { margin-top: 14px; }

/* 原始数据入口 */
.raw-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.raw-btn {
  background: none;
  border: 1px solid rgba(201,169,98,.5);
  border-radius: 4px;
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
  padding: 6px 14px;
  cursor: pointer;
  transition: all .25s ease;
}
.raw-btn:hover:not(:disabled) { background: var(--crimson); border-color: var(--crimson); color: var(--foreground); }
.raw-btn:disabled { opacity: .5; cursor: wait; }
.raw-hint { font-size: 12px; color: var(--muted-foreground); }
.raw-body { margin-top: 10px; }
.raw-error { color: #D98A8A; font-size: 14px; }
</style>