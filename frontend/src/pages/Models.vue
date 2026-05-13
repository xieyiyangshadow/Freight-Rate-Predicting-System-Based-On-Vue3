<template>
  <div class="content-wrap">
    <div class="toolbar-row">
      <div>
        <h2 class="section-title">预测模型</h2>
        <p class="section-subtitle">上传模型文件、查看训练状态和模型详情。</p>
      </div>
      <el-button type="primary" plain @click="refresh">刷新列表</el-button>
    </div>

    <div class="hero-grid">
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge">总览</div>
          <el-statistic :value="summary.total" title="模型总数" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(21, 128, 61, 0.10); color: var(--success);">完成</div>
          <el-statistic :value="summary.completed" title="训练完成" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(15, 118, 110, 0.10); color: var(--accent);">训练中</div>
          <el-statistic :value="summary.training" title="正在训练" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(185, 28, 28, 0.10); color: var(--danger);">失败</div>
          <el-statistic :value="summary.failed" title="训练失败" />
        </div>
      </el-card>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="8">
        <el-card class="surface-card" shadow="never">
          <template #header>
            <div class="toolbar-row">
              <strong>上传模型</strong>
              <span class="muted-text">系统会自动保存模型并开始训练模拟流程。</span>
            </div>
          </template>

          <el-form :model="form" label-position="top" class="stack">
            <el-form-item label="模型名称">
              <el-input v-model="form.name" placeholder="请输入模型名称" />
            </el-form-item>
            <el-form-item label="选择数据集 (可选)">
              <el-select v-model="form.dataset" placeholder="选择已有数据集" @change="onDatasetChange">
                <el-option v-for="d in datasets" :key="d.id" :label="d.name" :value="d.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="目标列 (target)">
              <el-select v-model="form.target_column" placeholder="选择目标列">
                <el-option v-for="c in availableColumns" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
            <el-form-item label="模型文件">
              <el-upload
                :auto-upload="false"
                :show-file-list="true"
                :limit="1"
                :on-change="handleFileChange"
              >
                <el-button>选择模型文件</el-button>
              </el-upload>
            </el-form-item>
            <div class="auth-actions">
              <el-button type="primary" :loading="loading" @click="uploadModel">上传并训练</el-button>
              <span class="muted-text">训练完成后可用于预测任务。</span>
            </div>
          </el-form>
        </el-card>

        <el-card class="surface-card" shadow="never" style="margin-top: 16px;">
          <template #header><strong>状态分布</strong></template>
          <div class="stack" style="gap: 12px;">
            <div v-for="item in statusSummary" :key="item.key" class="status-line">
              <div class="status-line-head">
                <span>{{ item.label }}</span>
                <strong>{{ item.count }}</strong>
              </div>
              <div class="status-track">
                <div class="status-fill" :class="item.key" :style="{ width: item.percent + '%' }"></div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="16">
        <el-card class="surface-card" shadow="never">
          <template #header>
            <div class="toolbar-row">
              <strong>模型列表</strong>
              <span class="muted-text">点击“详情”查看权重大小、训练指标与状态信息。</span>
            </div>
          </template>

          <el-table :data="models" class="responsive-table" empty-text="暂无模型记录">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column prop="name" label="名称" min-width="180" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="training_time" label="训练时长(秒)" width="140" />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="openDetail(scope.row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-drawer v-model="detailVisible" title="模型详情" size="40%">
      <div v-if="detail" class="stack">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="名称">{{ detail.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
          <el-descriptions-item label="权重路径">{{ detail.file_path }}</el-descriptions-item>
          <el-descriptions-item label="模型大小">{{ detail.file_size_bytes }} bytes</el-descriptions-item>
          <el-descriptions-item label="训练时长">{{ detail.training_time || '-' }} 秒</el-descriptions-item>
        </el-descriptions>
        <el-card class="surface-card" shadow="never">
          <template #header><strong>训练指标</strong></template>
          <pre class="detail-pre">{{ detail.metrics_text || '暂无指标文件' }}</pre>
        </el-card>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import api from '../api'
import { getDatasets, getDataset } from '../api'

export default {
  data() {
    return {
      loading: false,
      models: [],
      detailVisible: false,
      detail: null,
      file: null,
      form: {
        name: '',
        dataset: null,
        target_column: '',
      },
    }
  },
  computed: {
    summary() {
      return this.models.reduce((accumulator, item) => {
        accumulator.total += 1
        accumulator[item.status] = (accumulator[item.status] || 0) + 1
        return accumulator
      }, { total: 0, uploading: 0, training: 0, completed: 0, failed: 0 })
    },
    statusSummary() {
      const total = Math.max(this.summary.total, 1)
      return [
        { key: 'completed', label: '训练完成', count: this.summary.completed, percent: Math.round((this.summary.completed / total) * 100) },
        { key: 'training', label: '正在训练', count: this.summary.training, percent: Math.round((this.summary.training / total) * 100) },
        { key: 'uploading', label: '上传中', count: this.summary.uploading, percent: Math.round((this.summary.uploading / total) * 100) },
        { key: 'failed', label: '训练失败', count: this.summary.failed, percent: Math.round((this.summary.failed / total) * 100) },
      ]
    },
  },
  async mounted() {
    await this.refresh()
    await this.loadDatasets()
  },
  methods: {
    async refresh() {
      const res = await api.get('/models/')
      this.models = res.data
    },
    async loadDatasets() {
      try {
        const res = await getDatasets()
        this.datasets = res.data
      } catch (e) {
        this.datasets = []
      }
    },
    handleFileChange(uploadFile) {
      this.file = uploadFile.raw
    },
    async uploadModel() {
      if (!this.form.name || !this.file) {
        this.$message.warning('请填写模型名称并选择文件')
        return
      }
      const formData = new FormData()
      formData.append('name', this.form.name)
      if (this.form.dataset) formData.append('dataset', this.form.dataset)
      if (this.form.target_column) formData.append('target_column', this.form.target_column)
      formData.append('file', this.file)
      this.loading = true
      try {
        await api.post('/models/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        this.$message.success('模型已上传，训练已开始')
        this.form.name = ''
        this.form.dataset = null
        this.form.target_column = ''
        this.file = null
        await this.refresh()
      } catch (error) {
        this.$message.error(error?.response?.data?.detail || '上传失败')
      } finally {
        this.loading = false
      }
    },
    async onDatasetChange() {
      if (!this.form.dataset) { this.form.target_column = ''; return }
      const res = await getDataset(this.form.dataset)
      this.availableColumns = res.data.columns_list || []
      if (this.availableColumns.length && !this.availableColumns.includes(this.form.target_column)) {
        this.form.target_column = this.availableColumns[0]
      }
    },
    async openDetail(row) {
      const res = await api.get(`/models/${row.id}/`)
      this.detail = res.data
      this.detailVisible = true
    },
    statusTagType(status) {
      const map = {
        uploading: 'warning',
        training: 'info',
        completed: 'success',
        failed: 'danger',
      }
      return map[status] || 'info'
    },
  },
}
</script>

<style scoped>
.detail-pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  color: var(--text);
}

.status-line {
  display: grid;
  gap: 8px;
}

.status-line-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.status-track {
  width: 100%;
  height: 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.status-fill {
  height: 100%;
  border-radius: inherit;
}

.status-fill.completed {
  background: linear-gradient(90deg, var(--success), #53c47f);
}

.status-fill.training {
  background: linear-gradient(90deg, var(--accent), #40c1ba);
}

.status-fill.uploading {
  background: linear-gradient(90deg, var(--accent-2), #f97316);
}

.status-fill.failed {
  background: linear-gradient(90deg, var(--danger), #ef4444);
}
</style>