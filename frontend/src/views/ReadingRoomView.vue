<template>
  <div ref="viewEl" class="view reading-room">
    <header class="page-head">
      <div class="display-label">I · Analysis</div>
      <div class="title-line">
        <h1>探析 <span class="brass">· 智能问答</span></h1>
        <span v-if="store.currentDataset" class="badge">
          <span class="dot"></span>{{ store.currentDataset }}
        </span>
      </div>
      <p class="sub">以自然语言向数据提问，Agent 将自动撰写 SQL 并呈上图表与结论。</p>
    </header>

    <!-- 空数据提示 -->
    <div v-if="!store.hasDatasets" class="empty-state panel corner-flourish">
      <span class="mark">❧</span>
      <h3>镜中尚无数据</h3>
      <p>请先在左侧载入一份 CSV 数据集，再回到这里开始提问。</p>
      <router-link to="/archives" class="btn btn-brass" style="margin-top:18px;">前往数据集</router-link>
    </div>

    <!-- 聊天记录 -->
    <div v-else ref="scrollBox" class="chat-scroll">
      <ChatMessage v-for="(msg, i) in store.messages" :key="i" :message="msg" />

      <div v-if="store.sending" class="thinking">
        <span class="ornament">✒</span>
        <span>正在研读数据</span><span class="dots"></span>
      </div>
    </div>

    <!-- 输入区 -->
    <footer v-if="store.hasDatasets" class="composer">
      <textarea
        ref="textInput"
        class="input"
        v-model="draft"
        rows="1"
        placeholder="提出问题，例如：哪个地区销售额最高？"
        @keydown.enter.exact.prevent="submit"
        @input="autoResize"
      ></textarea>
      <button class="btn btn-brass send" :disabled="store.sending || !draft.trim()" @click="submit">
        <span>✉ 呈送</span>
      </button>
    </footer>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useAppStore } from '@/store'
import ChatMessage from '@/components/ChatMessage.vue'

const store = useAppStore()
const draft = ref('')
const scrollBox = ref(null)
const textInput = ref(null)
let scrollTimers = []

function scrollToBottom() {
  const el = scrollBox.value
  if (el) el.scrollTop = el.scrollHeight
}

// 图表/表格渲染会使高度延迟变化，安排多次滚动保证落到最新问答底部
function scheduleScroll() {
  scrollTimers.forEach((t) => clearTimeout(t))
  scrollTimers = []
  nextTick(scrollToBottom)
  scrollTimers.push(setTimeout(scrollToBottom, 60))
  scrollTimers.push(setTimeout(scrollToBottom, 250))
  scrollTimers.push(setTimeout(scrollToBottom, 800))
}

async function submit() {
  const text = draft.value.trim()
  if (!text || store.sending) return
  draft.value = ''
  autoResize()
  scheduleScroll()
  await store.sendMessage(text)
  scheduleScroll()
  textInput.value?.focus()
}

function autoResize() {
  const el = textInput.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

// 每次新增问答（用户提问或 AI 回答到达）都自动跳转到最新区域
watch(() => store.messages.length, scheduleScroll)
watch(() => store.sending, (sending) => {
  if (!sending) scheduleScroll()
})

onBeforeUnmount(() => {
  scrollTimers.forEach((t) => clearTimeout(t))
})
</script>

<style scoped>
/* 覆盖 .view 的 overflow-y:auto，改为内部 .chat-scroll 滚动，
   保证发送后能准确滚动到最新问答并让输入区固定在底部 */
.reading-room {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 8px 6px 24px;
  display: flex;
  flex-direction: column;
}

.composer {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  padding-top: 18px;
  border-top: 1px solid var(--border);
  background: linear-gradient(180deg, transparent, rgba(28,23,20,.8) 40%);
}
.composer textarea { resize: none; flex: 1; line-height: 1.5; }
.composer .send { flex-shrink: 0; margin-bottom: 0; }
</style>