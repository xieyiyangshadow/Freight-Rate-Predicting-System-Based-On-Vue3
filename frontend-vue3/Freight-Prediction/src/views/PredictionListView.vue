<template>
  <div class="prediction-list">
    <h1>预测任务</h1>

    <div class="actions-bar">
      <button @click="router.push('/predictions/new')">➕ 新建预测任务</button>
    </div>

    <div class="card">
      <div v-if="predictionStore.isLoading" class="loading">加载中...</div>
      <table v-else-if="predictionStore.tasks.length">
        <thead>
          <tr>
            <th>任务名称</th>
            <th>状态</th>
            <th>数据集</th>
            <th>模型数</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in predictionStore.tasks" :key="task.task_id">
            <td>{{ task.task_name }}</td>
            <td>
              <span class="status-badge" :class="task.status">
                {{ statusText(task.status) }}
              </span>
            </td>
            <td>{{ task.dataset }}</td>
            <td>{{ task.models_info?.length || 0 }}</td>
            <td>{{ formatDate(task.create_time) }}</td>
            <td>
              <button class="btn-primary" @click="viewResult(task.task_id)">
                查看结果
              </button>
              <button class="btn-danger" @click="confirmDelete(task.task_id)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">暂无预测任务</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePredictionStore } from '@/stores/prediction'

const router = useRouter()
const predictionStore = usePredictionStore()

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

const viewResult = (taskId: string) => {
  router.push(`/predictions/${taskId}`)
}

onMounted(() => {
  predictionStore.fetchTasks()
})

const confirmDelete = async (taskId: string) => {
  if (!confirm('确认删除该预测任务？此操作不可恢复。')) return
  try {
    await predictionStore.deletePredictionTask(taskId)
  } catch (err) {
    alert('删除失败')
  }
}
</script>

<style scoped>
.prediction-list { max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 20px; font-size: 24px; }
.actions-bar { margin-bottom: 20px; }
.card { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
button { padding: 10px 20px; background: #409eff; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
.btn-primary { padding: 6px 12px; font-size: 13px; }
.btn-danger { padding: 6px 12px; font-size: 13px; margin-left: 8px; background: #f56c6c; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ebeef5; }
th { color: #909399; font-weight: 500; }
.status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
.status-badge.pending { background: #fdf6ec; color: #e6a23c; }
.status-badge.running { background: #ecf5ff; color: #409eff; }
.status-badge.completed { background: #f0f9eb; color: #67c23a; }
.status-badge.failed { background: #fef0f0; color: #f56c6c; }
.loading, .empty { text-align: center; padding: 40px; color: #909399; }
</style>