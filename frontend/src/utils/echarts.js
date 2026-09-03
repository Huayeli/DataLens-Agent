import * as echarts from 'echarts'

// ==========================================
// ECharts Academia 主题
// 与全局设计令牌保持一致（黄铜/绯红/羊皮纸）
// ==========================================

export function registerAcademiaTheme() {
  echarts.registerTheme('academia', {
    backgroundColor: 'transparent',
    color: ['#C9A962', '#8B2635', '#9C8B7A', '#D4B872', '#6B5B4E', '#B8953F'],
    textStyle: {
      color: '#9C8B7A',
      fontFamily: "'Crimson Pro', Georgia, serif",
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: '#4A3F35' } },
      axisTick: { lineStyle: { color: '#4A3F35' } },
      axisLabel: { color: '#9C8B7A' },
      splitLine: { show: false },
    },
    valueAxis: {
      axisLine: { lineStyle: { color: '#4A3F35' } },
      axisLabel: { color: '#9C8B7A' },
      splitLine: { lineStyle: { color: 'rgba(74,63,53,0.5)' } },
    },
    legend: {
      textStyle: { color: '#9C8B7A' },
    },
    tooltip: {
      backgroundColor: '#251E19',
      borderColor: '#C9A962',
      borderWidth: 1,
      textStyle: { color: '#E8DFD4' },
      extraCssText: 'box-shadow: 0 8px 24px rgba(0,0,0,.4);',
    },
  })
}

// 截断过长分类名，只显示前若干字符，全称保留给 tooltip
function truncateLabel(value, max = 12) {
  const chars = Array.from(String(value ?? ''))
  if (chars.length <= max) return String(value)
  return chars.slice(0, max).join('') + '…'
}

export function buildChartOption(data, type, xKey, yKey, { allowFull = false } = {}) {
  if (!Array.isArray(data) || data.length === 0) return null
  const keys = Object.keys(data[0])
  const x = xKey || keys[0]
  const y = yKey || keys[1] || keys[0]
  const isLine = type === 'line'
  const categories = data.map((d) => d[x])
  const total = categories.length
  const many = total > 20

  const option = {
    tooltip: {
      trigger: 'axis',
      // 弹窗始终显示分类全称与数值
      formatter(params) {
        const p = Array.isArray(params) ? params[0] : params
        if (!p) return ''
        return `${p.name}<br/>${p.marker ?? ''}${p.seriesName}: ${p.value}`
      },
    },
    grid: { left: 12, right: 16, top: 8, bottom: many && allowFull ? 56 : 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: '#9C8B7A',
        rotate: many && !allowFull ? 30 : 0,
        fontFamily: "'Crimson Pro', Georgia, serif",
        // 标签只显示特征片段，完整名称通过悬浮弹窗查看
        formatter: (value) => truncateLabel(value, 12),
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#9C8B7A' },
    },
    series: [
      {
        name: y,
        type: isLine ? 'line' : 'bar',
        data: data.map((d) => Number(d[y]) || 0),
        smooth: isLine,
        symbol: isLine ? 'circle' : 'none',
        symbolSize: 7,
        lineStyle: { color: '#C9A962', width: 2 },
        itemStyle: {
          color: isLine
            ? '#C9A962'
            : new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#D4B872' },
                { offset: 1, color: '#8B6F2E' },
              ]),
          borderRadius: isLine ? 0 : [2, 2, 0, 0],
        },
        emphasis: {
          itemStyle: { color: '#8B2635' },
          lineStyle: { color: '#8B2635' },
        },
      },
    ],
  }

  // 分类较多且展开全部时，提供缩放条，保证可读性
  if (many && allowFull) {
    option.dataZoom = [
      { type: 'inside', start: 0, end: 100 },
      { type: 'slider', height: 16, bottom: 4, borderColor: '#4A3F35', fillerColor: 'rgba(201,169,98,.15)', handleStyle: { color: '#C9A962' }, textStyle: { color: '#9C8B7A' } },
    ]
  }

  return option
}