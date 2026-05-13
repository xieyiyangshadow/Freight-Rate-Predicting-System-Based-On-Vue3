<template>
  <div class="content-wrap">
    <div class="toolbar-row">
      <div>
        <h2 class="section-title">运价预测</h2>
        <p class="section-subtitle">选择出发地、目的地以及多个已完成模型，创建新的预测任务。</p>
      </div>
      <el-button type="primary" plain @click="refreshModels">刷新模型</el-button>
    </div>

    <div class="hero-grid">
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge">模型池</div>
          <el-statistic :value="summary.total" title="模型总数" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(21, 128, 61, 0.10); color: var(--success);">可用</div>
          <el-statistic :value="summary.ready" title="可用于预测" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(15, 118, 110, 0.10); color: var(--accent);">已选</div>
          <el-statistic :value="form.models.length" title="当前选择" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 3;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(194, 65, 12, 0.10); color: var(--accent-2);">建议</div>
          <div class="preview-status">
            <strong>任务状态</strong>
            <span>{{ selectionHint }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="10">
        <el-card class="surface-card" shadow="never">
          <template #header>
            <div class="toolbar-row">
              <strong>新建任务</strong>
              <span class="muted-text">仅可选择状态为 completed 的模型。</span>
            </div>
          </template>

          <el-form :model="form" label-position="top">
            <el-form-item label="任务名称">
              <el-input v-model="form.name" placeholder="请输入任务名称" />
            </el-form-item>
            <el-form-item label="出发地">
              <el-input v-model="form.origin" placeholder="请输入出发地" />
            </el-form-item>
            <el-form-item label="目的地">
              <el-input v-model="form.destination" placeholder="请输入目的地" />
            </el-form-item>
            <el-form-item label="模型">
              <el-select v-model="form.models" multiple filterable collapse-tags placeholder="选择一个或多个模型">
                <el-option v-for="m in readyModels" :key="m.id" :label="`${m.name} #${m.id}`" :value="m.id" />
              </el-select>
            </el-form-item>
            <div class="auth-actions">
              <el-button type="primary" :loading="loading" @click="submit">创建预测任务</el-button>
              <el-button text @click="resetForm">清空</el-button>
            </div>
          </el-form>
        </el-card>

        <el-card class="surface-card" shadow="never" style="margin-top: 16px;">
          <template #header><strong>任务预览</strong></template>
          <div class="stack" style="gap: 12px;">
            <div class="preview-row">
              <span class="muted-text">路线</span>
              <strong>{{ routePreview }}</strong>
            </div>
            <div class="preview-row">
              <span class="muted-text">任务名称</span>
              <strong>{{ form.name || '未填写' }}</strong>
            </div>
            <div class="preview-row">
              <span class="muted-text">选择模型</span>
              <strong>{{ selectedModelNames || '未选择' }}</strong>
            </div>
            <div class="preview-row">
              <span class="muted-text">建议说明</span>
              <span>{{ previewDescription }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="14">
        <el-card class="surface-card" shadow="never">
          <template #header>
            <div class="toolbar-row">
              <strong>可用模型</strong>
              <span class="muted-text">当前仅展示训练完成的模型。</span>
            </div>
          </template>
          <el-table :data="readyModels" class="responsive-table" empty-text="暂无可用模型">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column prop="name" label="名称" min-width="180" />
            <el-table-column prop="status" label="状态" width="120" />
            <el-table-column prop="training_time" label="训练时长" width="120" />
          </el-table>
        </el-card>

        <el-card class="surface-card" shadow="never" style="margin-top: 16px;">
          <template #header>
            <div class="toolbar-row">
              <strong>模型选择列表</strong>
              <span class="muted-text">完成训练的模型可多选参与同一任务。</span>
            </div>
          </template>
          <div class="selection-list">
            <div v-for="model in readyModels" :key="model.id" class="selection-item" :class="{ active: form.models.includes(model.id) }" @click="toggleModel(model.id)">
              <div>
                <strong>{{ model.name }}</strong>
                <div class="muted-text">#{{ model.id }} · 训练时长 {{ model.training_time || '-' }} 秒</div>
              </div>
              <el-tag :type="form.models.includes(model.id) ? 'success' : 'info'">
                {{ form.models.includes(model.id) ? '已选' : '可选' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import api, { getDatasets } from '../api'

export default {
  data() {
    return {
      loading: false,
      models: [],
      datasets: [],
      form: {
        name: '',
        origin: '',
        destination: '',
        models: [],
      },
    }
  },
  computed: {
    readyModels() {
      return this.models.filter((item) => item.status === 'completed')
    },
    datasetMap() {
      const map = {}
      for (const d of this.datasets) map[d.id] = d
      return map
    },
    summary() {
      return {
        total: this.models.length,
        ready: this.readyModels.length,
      }
    },
    selectedModelNames() {
      if (!this.form.models.length) {
        return ''
      }
      return this.readyModels
        .filter((item) => this.form.models.includes(item.id))
        .map((item) => item.name)
        .join('、')
    },
    selectedTargets() {
      const picked = this.readyModels.filter((m) => this.form.models.includes(m.id))
      const set = new Set(picked.map((p) => p.target_column || ''))
      return Array.from(set).filter((s) => s !== '')
    },
    hasTargetMismatch() {
      return this.selectedTargets.length > 1
    },
    routePreview() {
      return this.form.origin && this.form.destination
        ? `${this.form.origin} → ${this.form.destination}`
        : '请先填写出发地与目的地'
    },
    selectionHint() {
      return this.form.models.length ? '可提交' : '待选择'
    },
    previewDescription() {
      if (!this.form.models.length) {
        return '请选择至少一个已完成模型后再创建任务。'
      }
      return `当前任务将由 ${this.form.models.length} 个模型共同参与预测，结果会自动进入历史记录。`
    },
  },
  async mounted() {
    await this.refreshModels()
    await this.loadDatasets()
  },
  methods: {
    async refreshModels() {
      const res = await api.get('/models/')
      this.models = res.data
      this.form.models = this.form.models.filter((id) => this.readyModels.some((item) => item.id === id))
    },
    async loadDatasets() {
      try {
        const res = await getDatasets()
        this.datasets = res.data
      } catch (e) {
        this.datasets = []
      }
    },
    toggleModel(modelId) {
      if (this.form.models.includes(modelId)) {
        this.form.models = this.form.models.filter((id) => id !== modelId)
        return
      }
      this.form.models = [...this.form.models, modelId]
    },
    resetForm() {
      this.form = { name: '', origin: '', destination: '', models: [] }
    },
    async submit() {
      if (!this.form.name || !this.form.origin || !this.form.destination || !this.form.models.length) {
        this.$message.warning('请补全任务信息并至少选择一个已完成模型')
        return
      }
      const doSubmit = async () => {
        this.loading = true
        try {
          await api.post('/predictions/', {
            name: this.form.name,
            origin: this.form.origin,
            destination: this.form.destination,
            models_used: this.form.models,
          })
          this.$message.success('预测任务创建成功')
          this.resetForm()
          this.$router.push('/history')
        } catch (error) {
          this.$message.error(error?.response?.data?.detail || '任务创建失败')
        } finally {
          this.loading = false
        }
      }

      if (this.hasTargetMismatch) {
        this.$confirm('所选模型目标列不一致，结果可能不可比。是否继续创建任务？', '目标不一致', { type: 'warning' })
          .then(() => doSubmit())
          .catch(() => {})
      } else {
        await doSubmit()
      }
    },
  },
}
</script>

<style scoped>
.preview-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.selection-list {
  display: grid;
  gap: 12px;
}

.preview-status {
  display: grid;
  gap: 4px;
}

.selection-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  background: rgba(255, 255, 255, 0.65);
}

.selection-item:hover {
  transform: translateY(-1px);
  border-color: rgba(15, 118, 110, 0.25);
}

.selection-item.active {
  background: rgba(15, 118, 110, 0.07);
  border-color: rgba(15, 118, 110, 0.32);
}
.model-meta { font-size: 12px; color: var(--muted); }
</style>