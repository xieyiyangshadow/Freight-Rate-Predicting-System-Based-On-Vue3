<script setup lang="ts">
import { computed, onMounted, unref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDatasetStore } from '@/stores/dataset'
import { useModelStore } from '@/stores/model'
import { usePredictionStore } from '@/stores/prediction'

const router = useRouter()
const authStore = useAuthStore()
const datasetStore = useDatasetStore()
const modelStore = useModelStore()
const predictionStore = usePredictionStore()

const quickCards = computed(() => [
  {
    title: '数据集',
    value: (datasetStore.datasetCount) ? datasetStore.datasetCount : (datasetStore.datasets?.length || 0),
    hint: '已上传的数据资产',
    action: '查看数据集',
    to: '/datasets',
  },
  {
    title: '模型',
    value: (modelStore.modelCount) ? modelStore.modelCount : (modelStore.models?.length || 0),
    hint: '训练与可用模型',
    action: '查看模型',
    to: '/models',
  },
  {
    title: '预测任务',
    value: predictionStore.tasks?.length || 0,
    hint: '历史与正在执行的任务',
    action: '查看任务',
    to: '/predictions',
  },
  {
    title: '训练中',
    value: modelStore.trainingModels ? modelStore.trainingModels.length : (modelStore.models ? modelStore.models.filter(m=> m.training_status === 'training' || m.training_status === 'pending').length : 0),
    hint: '需要关注的模型状态',
    action: '查看训练中模型',
    to: '/models',
  },
])

const recentModels = computed(() => {
  const arr = unref(modelStore.models) || []
  return Array.isArray(arr) ? arr.slice(0, 5) : []
})

const recentTasks = computed(() => {
  const arr = unref(predictionStore.tasks) || []
  return Array.isArray(arr) ? arr.slice(0, 5) : []
})

const statusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    training: '训练中',
    completed: '已完成',
    failed: '训练失败',
  }

  return map[status] || status
}

const taskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '执行中',
    completed: '已完成',
    failed: '执行失败',
  }

  return map[status] || status
}

const formatDate = (value: string) => new Date(value).toLocaleString('zh-CN')

const goTo = (path: string) => router.push(path)

onMounted(async () => {
  if (!datasetStore.datasets?.length) {
    datasetStore.fetchDatasets().catch(() => undefined)
  }
  if (!modelStore.models?.length) {
    modelStore.fetchModels().catch(() => undefined)
  }
  if (!predictionStore.tasks?.length) {
    predictionStore.fetchTasks().catch(() => undefined)
  }
})
</script>

<template>
  <div class="dashboard">
    <section class="hero-card">
      <div>
        <p class="eyebrow">欢迎回来</p>
        <h1>你好，{{ authStore.user?.username || authStore.user?.email || '用户' }}</h1>
        <p class="hero-copy">
          这里是你的运价预测工作台。你可以从左侧导航进入数据集、模型和预测任务，
          也可以直接从下面的快捷卡片跳转到对应页面。
        </p>
      </div>

      <div class="hero-actions">
        <button type="button" @click="goTo('/datasets')">先上传数据集</button>
        <button type="button" class="secondary" @click="goTo('/models')">查看模型状态</button>
      </div>
    </section>

    <section class="stats-grid">
      <article v-for="card in quickCards" :key="card.title" class="stat-card" @click="goTo(card.to)">
        <span class="stat-title">{{ card.title }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
        <span class="stat-hint">{{ card.hint }}</span>
        <span class="stat-action">{{ card.action }}</span>
      </article>
    </section>

    <section class="content-grid">
      <div class="panel">
        <div class="panel-head">
          <h2>最近模型</h2>
          <button class="text-button" type="button" @click="goTo('/models')">查看全部</button>
        </div>

        <div v-if="recentModels.length" class="item-list">
          <button
            v-for="model in recentModels"
            :key="model.model_id"
            type="button"
            class="item-row"
            @click="goTo('/models')"
          >
            <div>
              <strong>{{ model.user_provided_name }}</strong>
              <p>{{ model.description || '暂无描述' }}</p>
            </div>
            <div class="item-meta">
              <span class="status-badge" :class="model.training_status">{{ statusText(model.training_status) }}</span>
              <small>{{ formatDate(model.create_time) }}</small>
            </div>
          </button>
        </div>
        <div v-else class="empty-state">暂无模型记录</div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <h2>最近任务</h2>
          <button class="text-button" type="button" @click="goTo('/predictions')">查看全部</button>
        </div>

        <div v-if="recentTasks.length" class="item-list">
          <button
            v-for="task in recentTasks"
            :key="task.task_id"
            type="button"
            class="item-row"
            @click="goTo(`/predictions/${task.task_id}`)"
          >
            <div>
              <strong>{{ task.task_name }}</strong>
              <p>{{ task.task_description || '暂无描述' }}</p>
            </div>
            <div class="item-meta">
              <span class="status-badge" :class="task.status">{{ taskStatusText(task.status) }}</span>
              <small>{{ formatDate(task.create_time) }}</small>
            </div>
          </button>
        </div>
        <div v-else class="empty-state">暂无预测任务</div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: 20px;
}

.hero-card,
.panel,
.stat-card {
  border: 1px solid rgba(112, 136, 176, 0.18);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 42px rgba(23, 40, 77, 0.08);
  backdrop-filter: blur(12px);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  border-radius: 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #56709a;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-card h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.2;
}

.hero-copy {
  max-width: 760px;
  margin: 14px 0 0;
  color: #51637c;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-self: center;
}

.hero-actions button,
.text-button {
  border: 0;
  border-radius: 14px;
  cursor: pointer;
}

.hero-actions button {
  min-width: 180px;
  padding: 14px 18px;
  background: linear-gradient(135deg, #2353ff 0%, #4b8dff 100%);
  color: #fff;
  font-weight: 700;
}

.hero-actions button.secondary {
  background: #eef4ff;
  color: #2157c7;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border-radius: 22px;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 52px rgba(23, 40, 77, 0.12);
}

.stat-title {
  color: #5a6f8b;
  font-size: 13px;
}

.stat-value {
  font-size: 32px;
  color: #13233c;
}

.stat-hint {
  color: #6b7d97;
  font-size: 13px;
}

.stat-action {
  color: #2353ff;
  font-size: 13px;
  font-weight: 600;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.panel {
  padding: 22px;
  border-radius: 26px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.panel-head h2 {
  margin: 0;
  font-size: 20px;
}

.text-button {
  padding: 8px 12px;
  background: #eef4ff;
  color: #2157c7;
  font-size: 13px;
  font-weight: 600;
}

.item-list {
  display: grid;
  gap: 12px;
}

.item-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  width: 100%;
  padding: 14px 16px;
  text-align: left;
  border: 1px solid #e6ecf6;
  border-radius: 18px;
  background: #fff;
  cursor: pointer;
}

.item-row strong {
  display: block;
  margin-bottom: 6px;
  color: #13233c;
}

.item-row p {
  margin: 0;
  color: #657690;
  font-size: 13px;
}

.item-meta {
  flex: none;
  display: grid;
  justify-items: end;
  gap: 8px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.pending,
.status-badge.training,
.status-badge.running {
  background: #eef4ff;
  color: #245dd0;
}

.status-badge.completed {
  background: #edf9f0;
  color: #2d9151;
}

.status-badge.failed {
  background: #fff1f0;
  color: #d84e4b;
}

.empty-state {
  padding: 24px 0 8px;
  color: #7a8aa2;
  text-align: center;
}

@media (max-width: 1180px) {
  .stats-grid,
  .content-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 820px) {
  .hero-card,
  .content-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    flex-direction: column;
  }

  .hero-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>
