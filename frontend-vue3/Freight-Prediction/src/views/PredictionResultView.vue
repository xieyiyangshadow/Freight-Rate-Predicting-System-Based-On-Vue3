<template>
  <div class="prediction-result">
    <h1>预测结果</h1>

    <div v-if="!task" class="loading">加载中...</div>
    <div v-else>
      <div class="card info-card">
        <h2>{{ task.task_name }}</h2>
        <p class="desc">{{ task.task_description || '无描述' }}</p>
        <div class="meta">
          <span>状态：<span class="status-badge" :class="task.status">{{ statusText(task.status) }}</span></span>
          <span>数据集：{{ task.dataset }}</span>
          <span>创建时间：{{ formatDate(task.create_time) }}</span>
        </div>
      </div>

      <div class="card result-card" v-if="task.status === 'completed'">
        <h2>各模型预测结果对比</h2>
        <div class="chart-wrapper">
          <canvas ref="chartCanvas" width="600" height="300"></canvas>
        </div>
        <table class="result-table">
          <thead>
            <tr>
              <th>模型名称</th>
              <th>预测值</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="model in task.models_info" :key="model.model_id">
              <td>{{ model.user_provided_name }}</td>
              <td>
                <span v-if="isSuccessResult(model.user_provided_name)" class="value success">
                  {{ getResultValue(model.user_provided_name) }}
                </span>
                <span v-else class="value error">
                  {{ getResultError(model.user_provided_name) }}
                </span>
              </td>
              <td>
                <span v-if="isSuccessResult(model.user_provided_name)" class="tag success">成功</span>
                <span v-else class="tag error">失败</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card" v-else-if="task.status === 'pending' || task.status === 'running'">
        <div class="running-status">
          <p>⏳ 预测任务正在执行中...</p>
          <button @click="refreshTask">刷新状态</button>
        </div>
      </div>

      <div class="card error-card" v-else-if="task.status === 'failed'">
        <p>❌ 任务执行失败</p>
      </div>

      <div class="actions-bar">
        <button @click="router.push('/predictions')">返回列表</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePredictionStore } from '@/stores/prediction'
import type { PredictionTask } from '@/types/prediction'
import Chart from 'chart.js/auto'

const route = useRoute()
const router = useRouter()
const predictionStore = usePredictionStore()

const task = ref(null as PredictionTask | null)
const taskId = route.params.id as string

const statusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '执行中',
    completed: '已完成',
    failed: '执行失败',
  }
  return map[status] || status
}

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString('zh-CN')

const isSuccessResult = (modelName: string) => {
  if (!task.value?.results) return false
  const result = task.value.results[modelName]
  return typeof result === 'number'
}

const getResultValue = (modelName: string) => {
  if (!task.value?.results) return '-'
  const result = task.value.results[modelName]
  return typeof result === 'number' ? result.toFixed(2) : '-'
}

const getResultError = (modelName: string) => {
  if (!task.value?.results) return '未知错误'
  const result = task.value.results[modelName]
  return typeof result === 'object' && result !== null ? (result as any).error || '未知错误' : '未知错误'
}

const refreshTask = async () => {
  const newTask = await predictionStore.refreshTask(taskId)
  if (newTask) {
    task.value = newTask
  }
}

const chartCanvas = ref<HTMLCanvasElement | null>(null)
let chartInstance: any = null

const renderChart = () => {
  if (!task.value) return
  const labels: string[] = []
  const data: number[] = []
  for (const m of task.value.models_info || []) {
    const name = m.user_provided_name
    const res = task.value.results?.[name]
    if (typeof res === 'number') {
      labels.push(name)
      data.push(Number(res))
    }
  }

  if (!chartCanvas.value) return
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  chartInstance = new Chart(chartCanvas.value.getContext('2d') as any, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: '预测值',
          data,
          backgroundColor: 'rgba(64,158,255,0.6)'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      }
    }
  })
}

onMounted(async () => {
  await refreshTask()
  if (task.value && (task.value.status === 'pending' || task.value.status === 'running')) {
    predictionStore.startPolling(taskId)
  }
  renderChart()
})

onUnmounted(() => {
  predictionStore.stopPolling()
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

watch(() => task.value?.results, () => {
  renderChart()
})
</script>

<style scoped>
.prediction-result { max-width: 800px; margin: 0 auto; }
h1 { margin-bottom: 20px; font-size: 24px; }
.card { background: #fff; border-radius: 8px; padding: 24px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
h2 { margin-bottom: 12px; font-size: 18px; color: #333; }
.desc { color: #666; margin-bottom: 12px; }
.meta { display: flex; gap: 20px; font-size: 14px; color: #666; }
.status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
.status-badge.pending { background: #fdf6ec; color: #e6a23c; }
.status-badge.running { background: #ecf5ff; color: #409eff; }
.status-badge.completed { background: #f0f9eb; color: #67c23a; }
.status-badge.failed { background: #fef0f0; color: #f56c6c; }
.result-table { width: 100%; border-collapse: collapse; }
.result-table th, .result-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ebeef5; }
.result-table th { color: #909399; font-weight: 500; }
.value { font-size: 18px; font-weight: 600; }
.value.success { color: #67c23a; }
.value.error { color: #f56c6c; font-size: 14px; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.tag.success { background: #f0f9eb; color: #67c23a; }
.tag.error { background: #fef0f0; color: #f56c6c; }
.running-status { text-align: center; padding: 40px; }
.running-status p { font-size: 16px; color: #666; margin-bottom: 16px; }
.error-card { background: #fef0f0; color: #f56c6c; text-align: center; padding: 40px; }
.actions-bar { margin-top: 20px; }
button { padding: 10px 20px; background: #409eff; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.loading { text-align: center; padding: 40px; color: #909399; }
.chart-wrapper { width: 100%; height: 320px; margin-bottom: 16px; }
</style>