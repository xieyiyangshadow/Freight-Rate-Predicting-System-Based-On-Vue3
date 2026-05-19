<template>
  <div class="dataset-view">
    <h1>数据集管理</h1>

    <!-- 上传卡片 -->
    <div class="card upload-card">
      <h2>上传新数据集</h2>
      <form @submit.prevent="handleUpload">
        <div class="form-row">
          <div class="form-group">
            <label>数据集名称 <span class="required">*</span></label>
            <input
              v-model="uploadForm.user_provided_name"
              type="text"
              placeholder="例如：上海-洛杉矶航线2024"
              required
            />
          </div>
          <div class="form-group">
            <label>描述</label>
            <input
              v-model="uploadForm.description"
              type="text"
              placeholder="可选"
            />
          </div>
        </div>

        <div class="form-group">
          <label>CSV 文件 <span class="required">*</span></label>
          <input
            type="file"
            accept=".csv"
            @change="handleFileChange"
            ref="fileInput"
            required
          />
          <small v-if="csvColumns.length" class="hint">
            检测到 {{ csvColumns.length }} 列：{{ csvColumns.join('、') }}
          </small>
          <small v-else class="hint">请选择 CSV 文件，系统将自动解析列名</small>
        </div>

        <div class="form-group" v-if="csvColumns.length">
          <label>目标列（Target）<<span class="required">*</span></label>
          <select v-model="uploadForm.target_column" required>
            <option value="" disabled>请选择目标列</option>
            <option v-for="col in csvColumns" :key="col" :value="col">
              {{ col }} {{ dataTypePreview[col] ? '（数值型）' : '（字符串型）' }}
            </option>
          </select>
        </div>

        <div class="actions">
          <button type="submit" :disabled="uploading || !canUpload">
            {{ uploading ? '上传并解析中...' : '上传数据集' }}
          </button>
        </div>
      </form>
    </div>

    <!-- 列表卡片 -->
    <div class="card list-card">
      <h2>我的数据集</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <table v-else-if="datasets.length">
        <thead>
          <tr>
            <th>用户命名</th>
            <th>系统文件名</th>
            <th>目标列</th>
            <th>列数</th>
            <th>数据类型</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ds in datasets" :key="ds.dataset_id">
            <td>{{ ds.user_provided_name }}</td>
            <td><code>{{ ds.sys_name }}</code></td>
            <td><span class="tag">{{ ds.target_column }}</span></td>
            <td>{{ ds.columns?.length || 0 }}</td>
            <td>
              <span
                v-for="(isNum, col) in ds.data_types"
                :key="col"
                class="type-badge"
                :class="{ numeric: isNum }"
              >
                {{ col }}:{{ isNum ? '数字' : '文本' }}
              </span>
            </td>
            <td>{{ formatDate(ds.create_time) }}</td>
            <td>
              <button class="btn-danger" @click="handleDelete(ds.dataset_id)">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">暂无数据集，请上传</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { uploadDataset, getDatasetList, deleteDataset } from '@/api/dataset'

interface Dataset {
  dataset_id: string
  user_provided_name: string
  description: string
  sys_name: string
  file_path: string
  columns: string[]
  target_column: string
  data_types: Record<string, boolean>
  create_time: string
  owner: number
}

const datasets = ref([] as Dataset[])
const loading = ref(false)
const uploading = ref(false)
const csvColumns = ref([] as string[])
const dataTypePreview = ref({} as Record<string, boolean>)
const fileInput = ref(null as HTMLInputElement | null)

const uploadForm = ref({
  user_provided_name: '',
  description: '',
  target_column: '',
  file: null as File | null,
})

const canUpload = computed(() => {
  return (
    uploadForm.value.user_provided_name &&
    uploadForm.value.target_column &&
    uploadForm.value.file
  )
})

// 前端简单解析 CSV 首行，提取列名并猜测数据类型
const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  uploadForm.value.file = file
  csvColumns.value = []
  dataTypePreview.value = {}

  const reader = new FileReader()
  reader.onload = (event) => {
    const text = event.target?.result as string
    if (!text) return

    const lines = text.split(/\r?\n/)
    if (lines.length < 1) return

    const headers = lines[0].split(',').map((c) => c.trim()).filter((c) => c)
    csvColumns.value = headers

    if (lines.length > 1 && lines[1]) {
      const sample = lines[1].split(',')
      headers.forEach((col, idx) => {
        const val = sample[idx]?.trim() || ''
        dataTypePreview.value[col] = val !== '' && !isNaN(Number(val))
      })
    }
  }
  reader.readAsText(file)
}

const fetchDatasets = async () => {
  loading.value = true
  try {
    const res = await getDatasetList()
    datasets.value = res.data.datasets || []
  } catch (err: any) {
    alert(err.response?.data?.message || '获取数据集列表失败')
  } finally {
    loading.value = false
  }
}

const handleUpload = async () => {
  if (!canUpload.value) return

  uploading.value = true
  const formData = new FormData()
  formData.append('user_provided_name', uploadForm.value.user_provided_name)
  formData.append('description', uploadForm.value.description)
  formData.append('file', uploadForm.value.file as File)
  formData.append('target_column', uploadForm.value.target_column)

  try {
    await uploadDataset(formData)
    alert('上传成功')
    uploadForm.value = {
      user_provided_name: '',
      description: '',
      target_column: '',
      file: null,
    }
    csvColumns.value = []
    dataTypePreview.value = {}
    if (fileInput.value) fileInput.value.value = ''
    fetchDatasets()
  } catch (err: any) {
    alert(err.response?.data?.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (datasetId: string) => {
  if (!confirm('确定删除该数据集？关联的模型和预测任务可能受影响。')) return
  try {
    await deleteDataset(datasetId)
    fetchDatasets()
  } catch (err: any) {
    alert(err.response?.data?.message || '删除失败')
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchDatasets()
})
</script>

<style scoped>
.dataset-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
h1 {
  margin-bottom: 20px;
  font-size: 24px;
}
.card {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
h2 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.form-group {
  margin-bottom: 16px;
}
label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}
.required {
  color: #f56c6c;
}
input,
select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}
input:focus,
select:focus {
  outline: none;
  border-color: #409eff;
}
.hint {
  display: block;
  margin-top: 6px;
  color: #909399;
  font-size: 12px;
}
.actions {
  margin-top: 8px;
}
button {
  padding: 10px 20px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-danger {
  background: #f56c6c;
  padding: 6px 12px;
  font-size: 13px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th,
td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}
th {
  color: #909399;
  font-weight: 500;
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
}
.type-badge {
  display: inline-block;
  margin-right: 6px;
  margin-bottom: 4px;
  padding: 2px 6px;
  background: #f4f4f5;
  color: #606266;
  border-radius: 4px;
  font-size: 11px;
}
.type-badge.numeric {
  background: #f0f9eb;
  color: #67c23a;
}
.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style>