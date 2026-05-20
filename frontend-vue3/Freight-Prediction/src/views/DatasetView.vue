<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'
import { useDatasetStore } from '@/stores/dataset'
import type { Dataset } from '@/types/dataset'

const datasetStore = useDatasetStore()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedDataset = ref<Dataset | null>(null)
const csvColumns = ref<string[]>([])
const dataTypePreview = ref<Record<string, boolean>>({})
const feedback = ref('')
const feedbackType = ref<'success' | 'error' | ''>('')
const uploadForm = ref({
  user_provided_name: '',
  description: '',
  target_column: '',
  file: null as File | null,
})

const histogramCanvas = ref<HTMLCanvasElement | null>(null)
let histogramChart: any = null

const allDatasets = computed(() => datasetStore.datasets ?? [])
const datasetDetail = computed(() => datasetStore.currentDatasetDetail)
const detailPreview = computed(() => datasetDetail.value?.preview || [])
const detailDescribe = computed(() => datasetDetail.value?.describe || {})
const detailHistograms = computed(() => datasetDetail.value?.histograms || {})
const detailCorrelation = computed(() => datasetDetail.value?.correlation || {})

const canUpload = computed(
  () => uploadForm.value.user_provided_name && uploadForm.value.target_column && uploadForm.value.file,
)

const currentColumns = computed(() => selectedDataset.value?.columns || [])
const numericColumns = computed(() => {
  const dataset = selectedDataset.value
  if (!dataset?.data_types) {
    return []
  }

  return Object.entries(dataset.data_types)
    .filter(([, isNumeric]) => isNumeric)
    .map(([column]) => column)
})

const showFeedback = (message: string, type: 'success' | 'error') => {
  feedback.value = message
  feedbackType.value = type
}

const selectDataset = async (dataset: Dataset | null) => {
  selectedDataset.value = dataset
  datasetStore.setCurrentDataset(dataset)
  if (dataset) {
    try {
      await datasetStore.fetchDatasetDetail(dataset.dataset_id)
    } catch {
      showFeedback('加载数据集详情失败，请稍后重试。', 'error')
    }
  }
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) {
    return
  }

  uploadForm.value.file = file
  csvColumns.value = []
  dataTypePreview.value = {}

  const reader = new FileReader()
  reader.onload = (readerEvent) => {
    const text = readerEvent.target?.result as string
    if (!text) {
      return
    }

    const lines = text.split(/\r?\n/)
    const headers = lines[0]?.split(',').map((column) => column.trim()).filter(Boolean) || []
    csvColumns.value = headers

    if (lines.length > 1 && lines[1]) {
      const sample = lines[1].split(',')
      headers.forEach((column, index) => {
        const value = sample[index]?.trim() || ''
        dataTypePreview.value[column] = value !== '' && !Number.isNaN(Number(value))
      })
    }
  }
  reader.readAsText(file)
}

const fetchDatasets = async () => {
  try {
    await datasetStore.fetchDatasets()
    if (!selectedDataset.value && allDatasets.value.length) {
      await selectDataset(allDatasets.value[0] || null)
    }
  } catch {
    showFeedback('获取数据集列表失败，请稍后重试。', 'error')
  }
}

const resetForm = () => {
  uploadForm.value = {
    user_provided_name: '',
    description: '',
    target_column: '',
    file: null,
  }
  csvColumns.value = []
  dataTypePreview.value = {}
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleUpload = async () => {
  if (!canUpload.value) {
    return
  }

  const formData = new FormData()
  formData.append('user_provided_name', uploadForm.value.user_provided_name)
  formData.append('description', uploadForm.value.description)
  formData.append('file', uploadForm.value.file as File)
  formData.append('target_column', uploadForm.value.target_column)

  try {
    await datasetStore.uploadDataset(formData)
    showFeedback('数据集上传成功，列表已同步刷新。', 'success')
    resetForm()
    await fetchDatasets()
  } catch (error: any) {
    showFeedback(error.response?.data?.message || '上传失败，请检查文件内容。', 'error')
  }
}

const handleDelete = async (datasetId: string) => {
  if (!window.confirm('确定删除该数据集？关联模型和任务可能会受到影响。')) {
    return
  }

  try {
    await datasetStore.deleteDataset(datasetId)
    if (selectedDataset.value?.dataset_id === datasetId) {
      await selectDataset(allDatasets.value[0] || null)
    }
    showFeedback('数据集已删除。', 'success')
  } catch (error: any) {
    showFeedback(error.response?.data?.message || '删除失败，请稍后重试。', 'error')
  }
}

const formatDate = (value: string) => new Date(value).toLocaleString('zh-CN')

const getCorrelationClass = (value: number) => {
  if (value >= 0.75) return 'strong-pos'
  if (value >= 0.35) return 'mid-pos'
  if (value <= -0.75) return 'strong-neg'
  if (value <= -0.35) return 'mid-neg'
  return 'neutral'
}

const renderHistogram = () => {
  const chartData = detailHistograms.value as Record<string, { counts: number[]; bin_edges: number[] }>
  const firstEntry = Object.entries(chartData)[0]
  const [column, histogram] = firstEntry || []

  if (!histogramCanvas.value || !column || !histogram) {
    if (histogramChart) {
      histogramChart.destroy()
      histogramChart = null
    }
    return
  }

  const labels = histogram.bin_edges.length > 1
    ? histogram.bin_edges.slice(0, -1).map((edge: number, index: number) => `${edge.toFixed(2)}~${histogram.bin_edges[index + 1].toFixed(2)}`)
    : []

  if (histogramChart) {
    histogramChart.destroy()
  }

  histogramChart = new Chart(histogramCanvas.value.getContext('2d') as CanvasRenderingContext2D, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: `${column} 分布`,
          data: histogram.counts,
          backgroundColor: 'rgba(54, 162, 235, 0.65)',
          borderRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  })
}

onMounted(fetchDatasets)

watch(
  () => datasetDetail.value,
  () => {
    renderHistogram()
  },
  { deep: true },
)

watch(
  () => selectedDataset.value?.dataset_id,
  async (datasetId) => {
    if (datasetId) {
      await datasetStore.fetchDatasetDetail(datasetId)
    }
  },
)

onUnmounted(() => {
  if (histogramChart) {
    histogramChart.destroy()
    histogramChart = null
  }
})
</script>

<template>
  <div class="page-grid">
    <section class="hero-card">
      <div>
        <p class="eyebrow">数据集管理</p>
        <h1>把原始 CSV 变成可追踪的训练资产</h1>
        <p>上传后可直接查看字段、目标列和数据类型，并通过右侧详情面板快速确认数据结构。</p>
      </div>
      <div class="summary-badges">
        <div class="summary-badge">
          <strong>{{ datasetStore.datasetCount }}</strong>
          <span>个数据集</span>
        </div>
        <div class="summary-badge">
          <strong>{{ selectedDataset ? currentColumns.length : 0 }}</strong>
          <span>当前列数</span>
        </div>
        <div class="summary-badge">
          <strong>{{ numericColumns.length }}</strong>
          <span>数值列</span>
        </div>
      </div>
    </section>

    <div v-if="feedback" class="feedback" :class="feedbackType">
      {{ feedback }}
    </div>

    <section class="content-grid">
      <div class="panel upload-panel">
        <div class="panel-head">
          <h2>上传新数据集</h2>
          <span>支持 CSV 自动解析</span>
        </div>

        <form class="form-grid" @submit.prevent="handleUpload">
          <div class="field">
            <label>数据集名称 <span class="required">*</span></label>
            <input v-model="uploadForm.user_provided_name" type="text" placeholder="例如：上海-洛杉矶航线2024" />
          </div>

          <div class="field">
            <label>描述</label>
            <input v-model="uploadForm.description" type="text" placeholder="可选" />
          </div>

          <div class="field field-full">
            <label>CSV 文件 <span class="required">*</span></label>
            <input ref="fileInput" type="file" accept=".csv" @change="handleFileChange" />
            <small v-if="csvColumns.length" class="hint">检测到 {{ csvColumns.length }} 列：{{ csvColumns.join('、') }}</small>
            <small v-else class="hint">上传后会自动解析首行列名，便于选择目标列。</small>
          </div>

          <div v-if="csvColumns.length" class="field field-full">
            <label>目标列（Target） <span class="required">*</span></label>
            <select v-model="uploadForm.target_column">
              <option value="" disabled>请选择目标列</option>
              <option v-for="column in csvColumns" :key="column" :value="column">
                {{ column }} {{ dataTypePreview[column] ? '（数值型）' : '（字符串型）' }}
              </option>
            </select>
          </div>

          <div class="actions field-full">
            <button type="submit" :disabled="datasetStore.isLoading || !canUpload">
              {{ datasetStore.isLoading ? '处理中...' : '上传数据集' }}
            </button>
          </div>
        </form>
      </div>

      <div class="panel list-panel">
        <div class="panel-head">
          <h2>我的数据集</h2>
          <span>{{ datasetStore.datasets.length }} 条记录</span>
        </div>

        <div v-if="datasetStore.isLoading && !datasetStore.datasets.length" class="loading-state">加载中...</div>
        <div v-else-if="datasetStore.datasets.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>名称</th>
                <th>目标列</th>
                <th>列数</th>
                <th>上传时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="dataset in datasetStore.datasets"
                :key="dataset.dataset_id"
                :class="{ active: selectedDataset?.dataset_id === dataset.dataset_id }"
              >
                <td>
                  <strong>{{ dataset.user_provided_name }}</strong>
                  <p>{{ dataset.description || '暂无描述' }}</p>
                </td>
                <td><span class="tag">{{ dataset.target_column }}</span></td>
                <td>{{ dataset.columns?.length || 0 }}</td>
                <td>{{ formatDate(dataset.create_time) }}</td>
                <td class="row-actions">
                  <button type="button" class="secondary" @click="selectDataset(dataset)">查看详情</button>
                  <button type="button" class="danger" @click="handleDelete(dataset.dataset_id)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">暂无数据集，请先上传一个 CSV 文件。</div>
      </div>
    </section>

    <section v-if="selectedDataset" class="panel detail-panel">
      <div class="panel-head">
        <h2>数据集详情</h2>
        <span>{{ selectedDataset.dataset_id }}</span>
      </div>

      <div class="detail-grid">
        <div class="detail-item">
          <span>系统文件名</span>
          <strong>{{ selectedDataset.sys_name }}</strong>
        </div>
        <div class="detail-item">
          <span>目标列</span>
          <strong>{{ selectedDataset.target_column }}</strong>
        </div>
        <div class="detail-item">
          <span>上传时间</span>
          <strong>{{ formatDate(selectedDataset.create_time) }}</strong>
        </div>
        <div class="detail-item">
          <span>文件路径</span>
          <strong>{{ selectedDataset.file_path }}</strong>
        </div>
      </div>

      <div class="detail-block">
        <h3>字段分布</h3>
        <div class="chart-card">
          <canvas ref="histogramCanvas"></canvas>
        </div>
        <div v-if="Object.keys(detailHistograms).length > 1" class="hint">当前只展示第一个数值字段的直方图，后续可切换为多图轮播。</div>
      </div>

      <div class="detail-block">
        <h3>样本预览</h3>
        <div class="preview-table-wrap">
          <table class="preview-table">
            <thead>
              <tr>
                <th v-for="column in currentColumns" :key="column">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in detailPreview" :key="index">
                <td v-for="column in currentColumns" :key="column">
                  {{ row[column] ?? '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="detail-block">
        <h3>字段类型</h3>
        <div class="chip-list">
          <span v-for="(isNumeric, column) in selectedDataset.data_types" :key="column" class="chip" :class="{ numeric: isNumeric }">
            {{ column }}：{{ isNumeric ? '数值' : '文本' }}
          </span>
        </div>
      </div>

      <div class="detail-block">
        <h3>数值字段统计</h3>
        <div v-if="Object.keys(detailDescribe).length" class="stats-grid">
          <div v-for="(stats, column) in detailDescribe" :key="column" class="stats-card">
            <div class="stats-title">{{ column }}</div>
            <div class="stats-row" v-for="(value, label) in stats" :key="label">
              <span>{{ label }}</span>
              <strong>{{ value === null ? '-' : Number(value).toFixed(4) }}</strong>
            </div>
          </div>
        </div>
        <div v-else class="empty-inline">当前数据集没有可用于统计的数值列。</div>
      </div>

      <div class="detail-block">
        <h3>相关性矩阵</h3>
        <div v-if="Object.keys(detailCorrelation).length" class="corr-wrap">
          <table class="corr-table">
            <thead>
              <tr>
                <th>字段</th>
                <th v-for="column in Object.keys(detailCorrelation)" :key="column">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rowName in Object.keys(detailCorrelation)" :key="rowName">
                <th>{{ rowName }}</th>
                <td
                  v-for="colName in Object.keys(detailCorrelation)"
                  :key="colName"
                  :class="getCorrelationClass(detailCorrelation[rowName]?.[colName] ?? 0)"
                >
                  {{ (detailCorrelation[rowName]?.[colName] ?? 0).toFixed(2) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-inline">当前数据集没有数值列，因此无法计算相关性矩阵。</div>
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
  grid-template-columns: 1fr 1.15fr;
  gap: 20px;
}

.panel {
  padding: 22px;
  border-radius: 26px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-head h2,
.detail-block h3 {
  margin: 0;
  color: #13233c;
}

.panel-head span {
  color: #6d7f98;
  font-size: 13px;
}

.form-grid {
  display: grid;
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
  color: #24364f;
}

.required {
  color: #d9534f;
}

input,
select {
  width: 100%;
  border: 1px solid #d8e0ec;
  border-radius: 14px;
  padding: 12px 14px;
  background: #fff;
  outline: none;
}

.hint {
  color: #76869c;
  font-size: 12px;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

button {
  border: none;
  border-radius: 12px;
  padding: 11px 18px;
  background: linear-gradient(135deg, #4f8df7, #3568d4);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.secondary {
  background: #eef3fb;
  color: #2e456a;
}

.danger {
  margin-left: 8px;
  background: #ff7070;
}

.table-wrap,
.preview-table-wrap,
.corr-wrap {
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 10px;
  border-bottom: 1px solid #edf1f6;
  text-align: left;
  vertical-align: top;
}

th {
  color: #61738e;
  font-weight: 600;
}

tr.active {
  background: #f7fbff;
}

.row-actions {
  white-space: nowrap;
}

.tag,
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: #eef4ff;
  color: #35588d;
  font-size: 12px;
}

.chip.numeric {
  background: #e8f8ee;
  color: #2d8d54;
}

.detail-panel {
  display: grid;
  gap: 20px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.detail-item {
  padding: 16px;
  border-radius: 18px;
  background: #f7f9fc;
}

.detail-item span {
  display: block;
  margin-bottom: 8px;
  color: #76869c;
  font-size: 12px;
}

.detail-item strong {
  color: #13233c;
  word-break: break-all;
}

.detail-block {
  display: grid;
  gap: 14px;
}

.chart-card {
  height: 260px;
  padding: 14px;
  border-radius: 18px;
  background: #f8fbff;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.stats-card {
  padding: 16px;
  border-radius: 18px;
  background: #f7f9fc;
  display: grid;
  gap: 8px;
}

.stats-title {
  font-weight: 700;
  color: #20324d;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #51637c;
  font-size: 13px;
}

.preview-table {
  min-width: 900px;
}

.preview-table td {
  max-width: 180px;
  word-break: break-word;
}

.corr-table {
  min-width: 720px;
}

.corr-table td,
.corr-table th {
  text-align: center;
}

.corr-table th:first-child,
.corr-table td:first-child {
  text-align: left;
  position: sticky;
  left: 0;
  background: #fff;
}

.strong-pos { background: #dff5e7; color: #207a41; }
.mid-pos { background: #eef9f0; color: #2d8d54; }
.neutral { background: #f7f9fc; color: #42566f; }
.mid-neg { background: #fff1f0; color: #d0605d; }
.strong-neg { background: #ffdedd; color: #b64443; }

.empty-state,
.loading-state,
.empty-inline {
  padding: 32px 0;
  color: #7b8ba2;
  text-align: center;
}

@media (max-width: 1100px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .hero-card {
    flex-direction: column;
  }

  .summary-badges {
    min-width: 0;
  }
}

@media (max-width: 720px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .summary-badges {
    grid-template-columns: 1fr;
  }
}
</style>
