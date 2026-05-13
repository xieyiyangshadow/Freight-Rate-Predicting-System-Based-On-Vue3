<template>
  <div class="content-wrap">
    <div class="toolbar-row">
      <div>
        <h2 class="section-title">数据集管理</h2>
        <p class="section-subtitle">上传 CSV 数据集，选择 target 列，查看数据内容。</p>
      </div>
      <el-button type="primary" plain @click="refresh">刷新列表</el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="8">
        <el-card class="surface-card">
          <template #header>
            <div class="toolbar-row"><strong>上传数据集</strong></div>
          </template>
          <el-form :model="form" label-position="top" class="stack">
            <el-form-item label="数据集名称">
              <el-input v-model="form.name" placeholder="示例: 物流样本数据" />
            </el-form-item>
            <el-form-item label="CSV 文件">
              <el-upload :auto-upload="false" :show-file-list="true" :limit="1" :on-change="handleFileChange">
                <el-button>选择 CSV</el-button>
              </el-upload>
            </el-form-item>
            
            <!-- Show column selector after file is chosen -->
            <div v-if="previewColumns.length > 0">
              <el-divider>列信息</el-divider>
              <el-form-item label="数据列">
                <el-tag v-for="col in previewColumns" :key="col" closable @close="removeColumn(col)" class="column-tag">
                  {{ col }}
                </el-tag>
              </el-form-item>
              <el-form-item label="选择 Target 列">
                <el-select v-model="form.target_column" placeholder="选择用于预测的目标列" clearable>
                  <el-option v-for="col in previewColumns" :key="col" :label="col" :value="col" />
                </el-select>
              </el-form-item>
            </div>

            <div class="auth-actions">
              <el-button type="primary" :loading="loading" @click="upload">上传</el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="16">
        <el-card class="surface-card">
          <template #header>
            <div class="toolbar-row"><strong>已上传数据集</strong></div>
          </template>
          <el-table :data="datasets" class="responsive-table" empty-text="暂无数据集">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column prop="name" label="名称" min-width="150" />
            <el-table-column label="Target 列" min-width="120">
              <template #default="{ row }">
                <el-tag v-if="row.target_column" type="success">{{ row.target_column }}</el-tag>
                <span v-else class="muted-text">未设置</span>
              </template>
            </el-table-column>
            <el-table-column label="列数" width="80" align="center">
              <template #default="{ row }">
                {{ parseColumns(row.columns).length }}
              </template>
            </el-table-column>
            <el-table-column prop="uploaded_at" label="上传时间" min-width="160" />
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="openDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Detail Drawer with Preview and Target Selection -->
    <el-drawer v-model="detailVisible" :title="`数据集详情 - ${detail?.name || ''}`" size="70%">
      <div v-if="detail" class="detail-content stack">
        <!-- Basic Info -->
        <el-card class="info-card">
          <template #header>
            <strong>基本信息</strong>
          </template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
            <el-descriptions-item label="数据集名称">{{ detail.name }}</el-descriptions-item>
            <el-descriptions-item label="上传时间">{{ detail.uploaded_at }}</el-descriptions-item>
            <el-descriptions-item label="数据行数">{{ detail.total_rows }}</el-descriptions-item>
          </el-descriptions>

          <!-- Target Column Selection -->
          <div style="margin-top: 16px;">
            <el-form :model="editForm" label-width="120px">
              <el-form-item label="Target 列">
                <el-select v-model="editForm.target_column" placeholder="选择目标列" @change="onTargetChange">
                  <el-option label="未设置" value="" />
                  <el-option v-for="col in detail.columns_list" :key="col" :label="col" :value="col" />
                </el-select>
              </el-form-item>
              <el-button v-if="editForm.target_column !== detail.target_column" type="primary" @click="saveTargetColumn">
                保存 Target 列
              </el-button>
            </el-form>
          </div>
        </el-card>

        <!-- Column List -->
        <el-card class="info-card">
          <template #header>
            <strong>数据列 ({{ detail.columns_list.length }})</strong>
          </template>
          <div class="columns-container">
            <el-tag v-for="col in detail.columns_list" :key="col" :type="col === detail.target_column ? 'success' : 'info'" style="margin: 4px;">
              {{ col }}
            </el-tag>
          </div>
        </el-card>

        <!-- Data Preview -->
        <el-card class="info-card" v-if="detail.data_preview.length > 0">
          <template #header>
            <strong>数据预览 (前 {{ detail.data_preview.length }} 行)</strong>
          </template>
          <el-table :data="detail.data_preview" max-height="400" class="responsive-table">
            <el-table-column v-for="col in detail.columns_list" :key="col" :prop="col" :label="col" min-width="120" />
          </el-table>
        </el-card>

        <el-alert v-else type="info" :closable="false">
          数据预览为空或文件格式错误
        </el-alert>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import { getDatasets, uploadDataset, getDataset, updateDataset } from '../api'

export default {
  data() {
    return {
      loading: false,
      datasets: [],
      file: null,
      form: { name: '', target_column: '' },
      previewColumns: [],
      detailVisible: false,
      detail: null,
      editForm: { target_column: '' }
    }
  },
  async mounted() {
    await this.refresh()
  },
  methods: {
    async refresh() {
      const res = await getDatasets()
      this.datasets = res.data
    },

    handleFileChange(file) {
      this.file = file.raw
      // Preview columns from file
      const reader = new FileReader()
      reader.onload = (e) => {
        const lines = e.target.result.split('\n')
        if (lines.length > 0) {
          this.previewColumns = lines[0].split(',').map(col => col.trim())
          this.form.target_column = '' // reset target selection
        }
      }
      reader.readAsText(this.file)
    },

    removeColumn(col) {
      const idx = this.previewColumns.indexOf(col)
      if (idx > -1) this.previewColumns.splice(idx, 1)
    },

    parseColumns(colJson) {
      try { return JSON.parse(colJson || '[]') } catch (e) { return [] }
    },

    async upload() {
      if (!this.form.name || !this.file) return this.$message.warning('请填写名称并选择文件')
      const fd = new FormData()
      fd.append('name', this.form.name)
      fd.append('file', this.file)
      if (this.form.target_column) {
        fd.append('target_column', this.form.target_column)
      }
      this.loading = true
      try {
        await uploadDataset(fd)
        this.$message.success('数据集上传成功')
        this.form.name = ''
        this.form.target_column = ''
        this.file = null
        this.previewColumns = []
        await this.refresh()
      } catch (err) {
        this.$message.error('上传失败')
      } finally { this.loading = false }
    },

    async openDetail(row) {
      try {
        const res = await getDataset(row.id)
        this.detail = res.data
        this.editForm.target_column = this.detail.target_column || ''
        this.detailVisible = true
      } catch (err) {
        this.$message.error('获取数据集详情失败')
      }
    },

    onTargetChange() {
      // Just for tracking changes
    },

    async saveTargetColumn() {
      try {
        await updateDataset(this.detail.id, { target_column: this.editForm.target_column })
        this.$message.success('Target 列已更新')
        this.detail.target_column = this.editForm.target_column
        await this.refresh()
      } catch (err) {
        this.$message.error('保存失败')
      }
    }
  }
}
</script>

<style scoped>
.muted-text { color: var(--muted); }
.column-tag { margin: 4px; }
.columns-container { display: flex; flex-wrap: wrap; }
.detail-content { max-height: 600px; overflow-y: auto; }
.info-card { margin-bottom: 12px; }
</style>
