<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useModelStore } from '@/stores/model'
import { useDatasetStore } from '@/stores/dataset'
import type { Model } from '@/types/model'

const modelStore = useModelStore()
const datasetStore = useDatasetStore()

const modelFileInput = ref<HTMLInputElement | null>(null)
const evalFileInput = ref<HTMLInputElement | null>(null)
const selectedModel = ref<Model | null>(null)
const feedback = ref('')
const feedbackType = ref<'success' | 'error' | ''>('')
const uploadForm = ref({
  user_provided_name: '',
  description: '',
  dataset_id: '',
  upload_mode: 'ready' as 'ready' | 'train',
  model_file: null as File | null,
  evaluation_file: null as File | null,
})



const completedModels = computed(() => modelStore.completedModels ?? [])

const trainingModels = computed(() => modelStore.trainingModels ?? [])

const failedModels = computed(() => modelStore.failedModels ?? [])

const allModels = computed(() => modelStore.models ?? [])

const canUpload = computed(() => {
  const base = uploadForm.value.user_provided_name && uploadForm.value.dataset_id && uploadForm.value.model_file
  if (uploadForm.value.upload_mode === 'ready') {
    return base && uploadForm.value.evaluation_file
  }
  return base
})

const showFeedback = (message: string, type: 'success' | 'error') => {
  feedback.value = message
  feedbackType.value = type
}

const statusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待训练',
    training: '训练中',
    completed: '已完成',
    failed: '训练失败',
  }

  return map[status] || status
}

const formatDate = (value: string) => new Date(value).toLocaleString('zh-CN')

const formatMetric = (value: number | null | undefined, digits = 3) => {
  if (value === null || value === undefined || Number.isNaN(value)) return '-'
  // 对大数值使用千分位显示并限制小数位
  try {
    const abs = Math.abs(value)
    if (abs >= 1000) {
      return Number(value).toLocaleString('zh-CN', { maximumFractionDigits: digits })
    }
    return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: digits, maximumFractionDigits: digits })
  } catch {
    return String(value)
  }
}

const selectModel = (model: Model | null) => {
  selectedModel.value = model
  modelStore.setCurrentModel(model)
}

const handleModelFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  uploadForm.value.model_file = target.files?.[0] || null
}

const handleEvalFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  uploadForm.value.evaluation_file = target.files?.[0] || null
}

const resetForm = () => {
  uploadForm.value = {
    user_provided_name: '',
    description: '',
    dataset_id: '',
    upload_mode: 'ready',
    model_file: null,
    evaluation_file: null,
  }

  if (modelFileInput.value) {
    modelFileInput.value.value = ''
  }
  if (evalFileInput.value) {
    evalFileInput.value.value = ''
  }
}

const handleUpload = async () => {
  if (!canUpload.value) {
    return
  }

  const formData = new FormData()
  formData.append('user_provided_name', uploadForm.value.user_provided_name)
  formData.append('description', uploadForm.value.description || '')
  formData.append('dataset_id', uploadForm.value.dataset_id)
  formData.append('upload_mode', uploadForm.value.upload_mode)
  formData.append('model_file', uploadForm.value.model_file as File)

  if (uploadForm.value.upload_mode === 'ready' && uploadForm.value.evaluation_file) {
    formData.append('evaluation_file', uploadForm.value.evaluation_file)
  }

  try {
    const response = await modelStore.uploadModel(formData)
    showFeedback('模型已提交，系统会自动刷新训练状态。', 'success')
    resetForm()
    await modelStore.fetchModels()
    const createdModel = response?.data?.model || allModels.value[0] || null
    if (createdModel) {
      selectModel(createdModel)
    }
    if (createdModel?.training_status === 'training' || createdModel?.training_status === 'pending') {
      modelStore.startPolling()
    }
  } catch (error: any) {
    showFeedback(error.response?.data?.message || '上传失败，请检查文件和后端返回。', 'error')
  }
}

const handleDelete = async (modelId: string) => {
  if (!window.confirm('确定删除该模型？')) {
    return
  }

  try {
    await modelStore.deleteModel(modelId)
    if (selectedModel.value?.model_id === modelId) {
      selectModel(allModels.value[0] || null)
    }
    showFeedback('模型已删除。', 'success')
  } catch (error: any) {
    showFeedback(error.response?.data?.message || '删除失败，请稍后重试。', 'error')
  }
}

const selectedMetrics = computed(() => {
  const raw = selectedModel.value?.metrics || null
  if (!raw) return null
  // 后端返回的 evaluation JSON 可能是完整对象，且里面包含一个 "metrics" 字段
  // 兼容两种形式：{ metrics: { r2_score: ... } } 或直接 { r2_score: ... }
  return (raw as any).metrics ?? raw
})

onMounted(async () => {
  try {
    await modelStore.fetchModels()
    if (!selectedModel.value && allModels.value.length) {
      selectModel(allModels.value[0] || null)
    }
    if (trainingModels.value.length) {
      modelStore.startPolling()
    }
  } catch {
    showFeedback('获取模型列表失败，请稍后重试。', 'error')
  }

  datasetStore.fetchDatasets().catch(() => undefined)
})
</script>

<template>
  <div class="page-grid">
    <section class="hero-card">
      <div>
        <p class="eyebrow">模型管理</p>
        <h1>查看训练中的模型、失败模型和已完成指标</h1>
        <p>上传后系统会根据后端状态持续刷新，你可以直接点开任意模型查看详情和指标。</p>
      </div>
      <div class="summary-badges">
        <div class="summary-badge">
          <strong>{{ modelStore.modelCount }}</strong>
          <span>个模型</span>
        </div>
        <div class="summary-badge">
          <strong>{{ trainingModels.length }}</strong>
          <span>训练中</span>
        </div>
        <div class="summary-badge">
          <strong>{{ failedModels.length }}</strong>
          <span>训练失败</span>
        </div>
      </div>
    </section>

    <div v-if="feedback" class="feedback" :class="feedbackType">
      {{ feedback }}
    </div>

    <section class="content-grid">
      <div class="panel upload-panel">
        <div class="panel-head">
          <h2>上传新模型</h2>
          <span>支持训练或直接部署</span>
        </div>

        <form class="form-grid" @submit.prevent="handleUpload">
          <div class="field">
            <label>模型名称 <span class="required">*</span></label>
            <input v-model="uploadForm.user_provided_name" type="text" placeholder="例如：XGBoost 基线模型" />
          </div>

          <div class="field">
            <label>描述</label>
            <input v-model="uploadForm.description" type="text" placeholder="可选" />
          </div>

          <div class="field">
            <label>关联数据集 <span class="required">*</span></label>
            <select v-model="uploadForm.dataset_id">
              <option value="" disabled>请选择数据集</option>
              <option v-for="dataset in datasetStore.datasets" :key="dataset.dataset_id" :value="dataset.dataset_id">
                {{ dataset.user_provided_name }}
              </option>
            </select>
          </div>

          <div class="field">
            <label>上传模式 <span class="required">*</span></label>
            <select v-model="uploadForm.upload_mode">
              <option value="ready">直接部署（已训练）</option>
              <option value="train">需要训练</option>
            </select>
          </div>

          <div class="field field-full">
            <label>模型文件 (.pkl / .joblib) <span class="required">*</span></label>
            <input ref="modelFileInput" type="file" accept=".pkl,.joblib" @change="handleModelFileChange" />
          </div>

          <div v-if="uploadForm.upload_mode === 'ready'" class="field field-full">
            <label>评估指标文件 (.json) <span class="required">*</span></label>
            <input ref="evalFileInput" type="file" accept=".json" @change="handleEvalFileChange" />
            <small class="hint">示例：包含 r2_score、mse、rmse、mae 等指标。</small>
          </div>

          <div class="actions field-full">
            <button type="submit" :disabled="modelStore.isLoading || !canUpload">
              {{ modelStore.isLoading ? '提交中...' : '上传模型' }}
            </button>
          </div>
        </form>
      </div>

      <div class="panel status-panel">
        <div class="panel-head">
          <h2>状态分组</h2>
          <span>点击即可查看详情</span>
        </div>

        <div class="group-grid">
          <button type="button" class="group-card training" @click="selectModel(trainingModels[0] || null)">
            <strong>{{ trainingModels.length }}</strong>
            <span>训练中 / 等待训练</span>
          </button>
          <button type="button" class="group-card failed" @click="selectModel(failedModels[0] || null)">
            <strong>{{ failedModels.length }}</strong>
            <span>训练失败</span>
          </button>
          <button type="button" class="group-card completed" @click="selectModel(completedModels[0] || null)">
            <strong>{{ completedModels.length }}</strong>
            <span>已完成</span>
          </button>
        </div>

        <div v-if="trainingModels.length" class="mini-list">
          <h3>正在训练</h3>
          <button v-for="model in trainingModels" :key="model.model_id" type="button" class="mini-row" @click="selectModel(model)">
            <span>{{ model.user_provided_name }}</span>
            <small>{{ statusText(model.training_status) }}</small>
          </button>
        </div>

        <div v-if="failedModels.length" class="mini-list">
          <h3>训练失败</h3>
          <button v-for="model in failedModels" :key="model.model_id" type="button" class="mini-row" @click="selectModel(model)">
            <span>{{ model.user_provided_name }}</span>
            <small>{{ statusText(model.training_status) }}</small>
          </button>
        </div>
      </div>
    </section>

    <section class="panel list-panel">
      <div class="panel-head">
        <h2>我的模型</h2>
        <span>{{ allModels.length }} 条记录</span>
      </div>

      <div v-if="modelStore.isLoading && !allModels.length" class="loading-state">加载中...</div>
      <div v-else-if="allModels.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>名称</th>
              <th>状态</th>
              <th>数据集</th>
              <th>上传时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="model in allModels"
              :key="model.model_id"
              :class="{ active: selectedModel?.model_id === model.model_id }"
            >
              <td>
                <strong>{{ model.user_provided_name }}</strong>
                <p>{{ model.description || '暂无描述' }}</p>
              </td>
              <td>
                <span class="status-badge" :class="model.training_status">{{ statusText(model.training_status) }}</span>
              </td>
              <td>{{ model.dataset_id }}</td>
              <td>{{ formatDate(model.create_time) }}</td>
              <td class="row-actions">
                <button type="button" class="secondary" @click="selectModel(model)">查看详情</button>
                <button type="button" class="danger" @click="handleDelete(model.model_id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="empty-state">暂无模型，请先上传一个模型文件。</div>
    </section>

    <section v-if="selectedModel" class="panel detail-panel">
      <div class="panel-head">
        <h2>模型详情</h2>
        <span>{{ selectedModel.model_id }}</span>
      </div>

      <div class="detail-grid">
        <div class="detail-item">
          <span>模型名称</span>
          <strong>{{ selectedModel.user_provided_name }}</strong>
        </div>
        <div class="detail-item">
          <span>关联数据集</span>
          <strong>{{ selectedModel.dataset_id }}</strong>
        </div>
        <div class="detail-item">
          <span>训练状态</span>
          <strong><span class="status-badge" :class="selectedModel.training_status">{{ statusText(selectedModel.training_status) }}</span></strong>
        </div>
        <div class="detail-item">
          <span>更新时间</span>
          <strong>{{ formatDate(selectedModel.update_time) }}</strong>
        </div>
      </div>

      <div class="detail-block">
        <h3>描述</h3>
        <p>{{ selectedModel.description || '暂无描述' }}</p>
      </div>

      <div class="detail-block">
        <h3>模型指标</h3>
        <div v-if="selectedMetrics" class="metrics-grid">
          <div class="metric-box"><span>R²</span><strong>{{ formatMetric(selectedMetrics.r2_score, 3) }}</strong></div>
          <div class="metric-box"><span>MSE</span><strong>{{ formatMetric(selectedMetrics.mse, 0) }}</strong></div>
          <div class="metric-box"><span>RMSE</span><strong>{{ formatMetric(selectedMetrics.rmse, 2) }}</strong></div>
          <div class="metric-box"><span>MAE</span><strong>{{ formatMetric(selectedMetrics.mae, 2) }}</strong></div>
        </div>
        <p v-else class="empty-inline">该模型尚未返回指标或正在训练中。</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-grid {
  display: grid;
  gap: 20px;
}

.hero-card,
.panel {
  border: 1px solid rgba(112, 136, 176, 0.18);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 18px 42px rgba(23, 40, 77, 0.08);
  backdrop-filter: blur(12px);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 26px 28px;
  border-radius: 26px;
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
  font-size: 32px;
}

.hero-card p {
  margin: 12px 0 0;
  max-width: 760px;
  line-height: 1.8;
  color: #51637c;
}

.summary-badges {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  min-width: 360px;
}

.summary-badge {
  display: grid;
  gap: 6px;
  padding: 16px;
  border-radius: 18px;
  background: #f6f9ff;
  text-align: center;
}

.summary-badge strong {
  font-size: 28px;
  color: #13233c;
}

.summary-badge span {
  color: #61738e;
  font-size: 13px;
}

.feedback {
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 14px;
}

.feedback.success {
  background: #edf9f0;
  color: #2d9151;
}

.feedback.error {
  background: #fff1f0;
  color: #d84e4b;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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
  margin-bottom: 18px;
}

.panel-head h2,
.detail-block h3 {
  margin: 0;
}

.panel-head span,
.detail-item span,
.detail-block h3 {
  color: #6a7d98;
  font-size: 13px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
}

.field-full {
  grid-column: 1 / -1;
}

label {
  font-size: 14px;
  color: #4a5c74;
}

.required {
  color: #d84e4b;
}

input,
select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #dfe7f3;
  border-radius: 14px;
  font-size: 14px;
  background: #fff;
}

.hint {
  color: #7b8da7;
  font-size: 12px;
}

.actions {
  display: flex;
}

button {
  border: 0;
  border-radius: 14px;
  cursor: pointer;
}

.actions button {
  padding: 13px 18px;
  background: linear-gradient(135deg, #2353ff 0%, #4b8dff 100%);
  color: #fff;
  font-weight: 700;
}

button.secondary,
button.danger {
  padding: 8px 12px;
  font-size: 13px;
}

button.secondary {
  background: #eef4ff;
  color: #2157c7;
}

button.danger {
  background: #fff1f0;
  color: #d84e4b;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}

.table-wrap {
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #edf1f7;
  vertical-align: top;
}

th {
  color: #6a7d98;
  font-size: 13px;
  font-weight: 600;
}

tbody tr.active {
  background: #f6f9ff;
}

td strong {
  display: block;
  margin-bottom: 6px;
  color: #13233c;
}

td p {
  margin: 0;
  color: #6d7f98;
  font-size: 13px;
}

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.pending,
.status-badge.training {
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

.group-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.group-card {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  text-align: left;
  color: #13233c;
  background: #f7faff;
}

.group-card strong {
  font-size: 28px;
}

.group-card.training {
  background: #eef4ff;
}

.group-card.failed {
  background: #fff1f0;
}

.group-card.completed {
  background: #edf9f0;
}

.mini-list {
  margin-top: 18px;
  display: grid;
  gap: 10px;
}

.mini-list h3 {
  margin: 0;
  font-size: 14px;
  color: #6a7d98;
}

.mini-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  width: 100%;
  padding: 12px 14px;
  background: #f7faff;
  color: #13233c;
}

.mini-row small {
  color: #6a7d98;
}

.detail-panel {
  display: grid;
  gap: 18px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.detail-item {
  padding: 16px;
  border-radius: 18px;
  background: #f7faff;
}

.detail-item strong {
  display: block;
  margin-top: 6px;
  color: #13233c;
  word-break: break-all;
}

.detail-block {
  display: grid;
  gap: 12px;
}

.detail-block p,
.empty-inline {
  margin: 0;
  color: #6d7f98;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.metric-box {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  background: #f7faff;
}

.metric-box span {
  color: #6a7d98;
  font-size: 13px;
}

.metric-box strong {
  color: #13233c;
  font-size: 22px;
}

.loading-state,
.empty-state {
  padding: 28px 0 8px;
  color: #7a8aa2;
  text-align: center;
}

@media (max-width: 1180px) {
  .content-grid,
  .hero-card {
    grid-template-columns: 1fr;
    display: grid;
  }

  .summary-badges {
    min-width: 0;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .form-grid,
  .detail-grid,
  .summary-badges,
  .group-grid,
  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    padding: 22px;
  }
}
</style>
