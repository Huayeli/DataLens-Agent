// ==========================================
// 与 FastAPI 后端通信的轻量封装
// 生产环境由后端托管 dist，因此使用相对路径
// ==========================================

async function request(path, options = {}) {
  const res = await fetch(path, options)
  if (!res.ok) {
    let detail = ''
    try {
      const body = await res.json()
      detail = body.detail || body.message || JSON.stringify(body)
    } catch {
      detail = await res.text().catch(() => '')
    }
    throw new Error(`请求失败 (HTTP ${res.status})：${detail}`)
  }
  return res.json()
}

export const api = {
  chat: (message, dataset) =>
    request('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, dataset }),
    }),

  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/upload', { method: 'POST', body: form })
  },

  datasets: () => request('/datasets'),

  switchDataset: (name) =>
    request(`/switch/${encodeURIComponent(name)}`, { method: 'POST' }),

  datasetStats: (name) =>
    request(`/datasets/${encodeURIComponent(name)}/stats`),

  deleteDataset: (name) =>
    request(`/datasets/${encodeURIComponent(name)}`, { method: 'DELETE' }),

  datasetData: (name) => request(`/data/${encodeURIComponent(name)}`),

  health: () => request('/health'),

  info: () => request('/info'),

  settings: () => request('/settings'),

  saveSettings: (payload) =>
    request('/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
}