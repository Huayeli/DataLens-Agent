<template>
  <div class="view">
    <header class="page-head">
      <div class="display-label">III · Settings</div>
      <div class="title-line">
        <h1>设置 <span class="brass">· 系统信息</span></h1>
      </div>
      <p class="sub">服务状态与模型配置。修改模型配置后无需重启，立即生效。</p>
    </header>

    <div class="settings-grid">
      <!-- 模型配置（可编辑） -->
      <section class="panel corner-flourish settings-card model-card">
        <div class="card-head">
          <span class="card-icon">✦</span>
          <div>
            <div class="display-label">Model</div>
            <h2>模型配置</h2>
          </div>
        </div>

        <div v-if="loaded" class="form">
          <label class="field">
            <span class="field-label">API 地址（API Base）</span>
            <input v-model.trim="form.api_base" class="input" placeholder="https://api.deepseek.com" autocomplete="off" />
          </label>

          <label class="field">
            <span class="field-label">模型名称（Model）</span>
            <input v-model.trim="form.model" class="input" placeholder="deepseek-chat" autocomplete="off" />
          </label>

          <label class="field">
            <span class="field-label">API 密钥（API Key）</span>
            <input
              v-model="form.api_key"
              type="password"
              class="input"
              :placeholder="keyHint"
              autocomplete="new-password"
            />
            <span class="field-hint" :class="{ ok: cfg?.has_api_key, warn: !cfg?.has_api_key }">
              {{ keyHint }}
            </span>
          </label>

          <div class="form-actions">
            <button class="btn btn-brass" :disabled="saving" @click="save">✒ 保存配置</button>
            <span v-if="saveMsg" class="save-msg" :class="saveOk ? 'ok' : 'err'">{{ saveMsg }}</span>
          </div>
        </div>
        <p v-else class="muted">正在读取…</p>
      </section>

      <!-- 服务状态 -->
      <section class="panel corner-flourish settings-card">
        <div class="card-head">
          <span class="card-icon">⚖</span>
          <div>
            <div class="display-label">Service</div>
            <h2>服务状态</h2>
          </div>
        </div>

        <div class="kv">
          <div class="kv-row"><span>Backend</span><span class="kv-val"><span class="status-dot" :class="health?.status"></span>{{ health?.status || '未知' }}</span></div>
          <div class="kv-row"><span>当前数据集</span><span class="kv-val brass">{{ health?.dataset || '—' }}</span></div>
          <div class="kv-row"><span>数据集总数</span><span class="kv-val">{{ health?.tables?.length ?? '—' }}</span></div>
        </div>
        <button class="btn btn-outline" style="width:100%;" @click="loadHealth">重新检测</button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { api } from '@/api'

const health = ref(null)
const cfg = ref(null)
const loaded = ref(false)
const saving = ref(false)
const saveMsg = ref('')
const saveOk = ref(true)

const form = reactive({ api_base: '', model: '', api_key: '' })

const keyHint = computed(() => {
  if (!cfg.value) return ''
  return cfg.value.has_api_key
    ? `已配置（${cfg.value.key_tail}），留空保持不变`
    : '未配置，请粘贴 API 密钥'
})

async function loadHealth() {
  try {
    health.value = await api.health()
  } catch {
    health.value = { status: 'offline' }
  }
}

async function loadSettings() {
  try {
    cfg.value = await api.settings()
    form.api_base = cfg.value.api_base
    form.model = cfg.value.model
    form.api_key = ''
    loaded.value = true
  } catch {
    loaded.value = false
  }
}

async function save() {
  saving.value = true
  saveMsg.value = ''
  try {
    const res = await api.saveSettings({
      api_base: form.api_base,
      model: form.model,
      api_key: form.api_key,
    })
    cfg.value = res.config
    form.api_key = ''
    saveOk.value = res.llm_ok
    saveMsg.value = res.llm_ok
      ? '配置已保存并生效'
      : '配置已保存，但 API 密钥为空或无效，模型暂不可用'
  } catch (error) {
    saveOk.value = false
    saveMsg.value = `Error: ${error.message}`
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadHealth()
  loadSettings()
})
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 18px;
}

.settings-card { padding: 24px 26px; }
.card-head { display: flex; gap: 14px; align-items: center; margin-bottom: 18px; }
.card-icon {
  width: 40px; height: 40px;
  border: 1.5px solid var(--accent);
  border-radius: 50%;
  display: grid; place-items: center;
  color: var(--accent);
  font-size: 17px;
  flex-shrink: 0;
}
.card-head h2 { font-size: 24px; }

.form { display: flex; flex-direction: column; gap: 16px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: .18em;
  font-size: 10px;
  color: var(--muted-foreground);
}
.field-hint { font-size: 13px; font-style: italic; }
.ok { color: #9DBF7E; }
.warn { color: #D4B872; }
.err { color: #D98A8A; }

.form-actions { display: flex; align-items: center; gap: 16px; margin-top: 4px; }
.save-msg { font-size: 14px; }

.kv { margin-bottom: 16px; }
.kv-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  padding: 9px 0;
  border-bottom: 1px solid rgba(74,63,53,.5);
  font-size: 15px;
}
.kv-row:last-child { border-bottom: none; }
.kv-val { font-family: var(--font-heading); font-size: 16px; text-align: right; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }
.status-dot.running { background: #7FA65A; box-shadow: 0 0 8px rgba(127,166,90,.8); }
.status-dot.offline { background: var(--crimson); }
code { color: var(--accent-bright); font-family: Consolas, monospace; font-size: 13px; }

</style>