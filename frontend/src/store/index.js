import { defineStore } from 'pinia'
import { api } from '@/api'

// ==========================================
// 全局状态：数据集、聊天记录、发送状态
// ==========================================

export const useAppStore = defineStore('app', {
  state: () => ({
    datasets: [],
    currentDataset: '',
    messages: [
      {
        role: 'ai',
        content:
          '欢迎使用「数镜」。载入一份 CSV 数据，即可用自然语言提问——镜中会浮现图表与结论。试试：「哪个地区销售额最高？」或「每月销售额的变化趋势如何？」',
      },
    ],
    sending: false,
    lastError: '',
  }),
  getters: {
    hasDatasets: (state) => state.datasets.length > 0,
  },
  actions: {
    async loadDatasets() {
      const data = await api.datasets()
      this.datasets = data.datasets || []
      this.currentDataset = data.current || ''
    },

    async switchDataset(name) {
      const data = await api.switchDataset(name)
      if (data.success) {
        this.currentDataset = name
        await this.loadDatasets()
        return true
      }
      return false
    },

    async uploadFile(file) {
      const data = await api.upload(file)
      if (data.success) {
        this.currentDataset = data.table
        await this.loadDatasets()
        return data
      }
      throw new Error(data.message || '上传失败')
    },

    async sendMessage(text) {
      this.messages.push({ role: 'user', content: text })
      this.sending = true
      this.lastError = ''
      try {
        const result = await api.chat(text, this.currentDataset)
        this.messages.push({
          role: 'ai',
          content: result.answer || '（未获得回答）',
          sql: result.sql || '',
          data: result.data || [],
          chart: result.chart || 'table',
          x: result.x || '',
          y: result.y || '',
          dataset: result.dataset || this.currentDataset || '',
        })
        if (result.dataset) this.currentDataset = result.dataset
      } catch (error) {
        this.lastError = error.message
        this.messages.push({
          role: 'ai',
          content: `Error: ${error.message}`,
          error: true,
        })
      } finally {
        this.sending = false
      }
    },
  },
})