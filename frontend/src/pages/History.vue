<template>
  <div class="content-wrap">
    <div class="toolbar-row">
      <div>
        <h2 class="section-title">历史预测</h2>
        <p class="section-subtitle">查看已完成的预测任务、任务详情和删除操作。</p>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <el-input v-model="searchQuery" placeholder="按名称搜索" size="small" clearable @clear="refresh" @input="applyLocalFilter" />
        <el-select v-model="statusFilter" placeholder="状态" size="small" clearable @change="applyLocalFilter">
          <el-option label="全部" :value="''" />
          <el-option label="completed" :value="'completed'" />
          <el-option label="running" :value="'running'" />
          <el-option label="pending" :value="'pending'" />
          <el-option label="failed" :value="'failed'" />
        </el-select>
        <el-button type="primary" plain @click="refresh">刷新任务</el-button>
      </div>
    </div>

    <el-card class="surface-card" shadow="never">
      <template #header>
        <div class="toolbar-row">
          <strong>任务列表</strong>
          <span class="muted-text">点击详情查看多模型预测结果，点击删除可移除任务。</span>
        </div>
      </template>

      <el-table :data="tasks" class="responsive-table" empty-text="暂无历史预测任务">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="origin" label="出发地" />
        <el-table-column prop="destination" label="目的地" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="openDetail(scope.row)">详情</el-button>
            <el-button type="danger" link @click="removeTask(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-drawer v-model="detailVisible" title="任务详情" size="42%">
      <div v-if="detail" class="stack">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:12px">
          <div />
          <div>
            <el-button size="small" @click="downloadResult">下载 JSON</el-button>
            <el-button size="small" type="danger" @click="() => removeTask(detail)">删除任务</el-button>
          </div>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="任务ID">{{ detail.id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ detail.name }}</el-descriptions-item>
          <el-descriptions-item label="出发地">{{ detail.origin }}</el-descriptions-item>
          <el-descriptions-item label="目的地">{{ detail.destination }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
          <el-descriptions-item label="模型ID列表">{{ (detail.models_used || []).join(', ') }}</el-descriptions-item>
          <el-descriptions-item label="输出目录">{{ detail.output_folder }}</el-descriptions-item>
        </el-descriptions>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-card class="surface-card compact-stat" shadow="never">
              <div class="muted-text">基准运价</div>
              <div class="detail-metric">{{ summary.base_fare ?? '-' }}</div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="surface-card compact-stat" shadow="never">
              <div class="muted-text">最优预测</div>
              <div class="detail-metric">{{ summary.best_predicted_fare ?? '-' }}</div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="surface-card compact-stat" shadow="never">
              <div class="muted-text">平均预测</div>
              <div class="detail-metric">{{ summary.average_predicted_fare ?? '-' }}</div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="surface-card compact-stat" shadow="never">
              <div class="muted-text">上下浮动</div>
              <div class="detail-metric">{{ summary.spread ?? '-' }}</div>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="surface-card" shadow="never">
          <template #header><strong>多模型对比图</strong></template>
          <div class="comparison-chart" v-if="comparisonRows.length">
            <div v-for="row in comparisonRows" :key="row.model_id" class="comparison-row">
              <div class="comparison-label">
                <strong>{{ row.model_name }}</strong>
                <span class="muted-text">#{{ row.model_id }}</span>
              </div>
              <div class="comparison-bar-track">
                <div class="comparison-bar" :style="{ width: row.barWidth + '%' }"></div>
              </div>
              <div class="comparison-values">
                <span>{{ row.predicted_fare }}</span>
                <span :class="row.delta >= 0 ? 'delta-up' : 'delta-down'">
                  {{ row.delta >= 0 ? '+' : '' }}{{ row.delta }} / {{ row.delta_pct }}%
                </span>
              </div>
            </div>
          </div>
          <div v-else class="muted-text">暂无对比数据</div>
        </el-card>

        <el-card class="surface-card" shadow="never">
          <template #header><strong>预测结果表</strong></template>
          <el-table :data="comparisonRows" class="responsive-table" empty-text="暂无结果数据">
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="model_name" label="模型" min-width="160" />
            <el-table-column prop="target_column" label="目标列" width="140">
              <template #default="scope">
                <el-tag v-if="scope.row.target_column">{{ scope.row.target_column }}</el-tag>
                <span v-else class="muted-text">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_fare" label="预测运价" width="120" />
            <el-table-column prop="delta" label="涨跌" width="120">
              <template #default="scope">
                <span :class="scope.row.delta >= 0 ? 'delta-up' : 'delta-down'">
                  {{ scope.row.delta >= 0 ? '+' : '' }}{{ scope.row.delta }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="delta_pct" label="涨跌幅" width="120">
              <template #default="scope">
                <span :class="scope.row.delta >= 0 ? 'delta-up' : 'delta-down'">
                  {{ scope.row.delta >= 0 ? '+' : '' }}{{ scope.row.delta_pct }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="120" />
          </el-table>
        </el-card>

        <el-card class="surface-card" shadow="never">
          <template #header><strong>原始结果 JSON</strong></template>
          <pre class="detail-pre">{{ prettyResult }}</pre>
        </el-card>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      tasksAll: [],
      tasks: [],
      detailVisible: false,
      detail: null,
      searchQuery: '',
      statusFilter: '',
    }
  },
  computed: {
    filteredTasks() {
      return this.tasks
    },
    summary() {
      return this.detail?.result_json?.summary || {}
    },
    comparisonRows() {
      const resultJson = this.detail?.result_json || {}
      const rows = Array.isArray(resultJson.models)
        ? resultJson.models
        : Object.entries(resultJson)
            .filter(([key]) => key !== 'summary')
            .map(([key, value], index) => ({
              model_id: Number(key),
              model_name: value.model_name || `模型 ${key}`,
              model_status: value.model_status || '-',
              predicted_fare: value.pred ?? value.predicted_fare ?? 0,
              delta: value.delta ?? 0,
              delta_pct: value.delta_pct ?? 0,
              confidence: value.confidence ?? '-',
              rank: value.rank ?? index + 1,
            }))
      if (!rows.length) {
        return []
      }
      const maxFare = Math.max(...rows.map((item) => item.predicted_fare))
      return rows.map((item) => ({
        ...item,
        barWidth: maxFare ? Math.max(18, Math.round((item.predicted_fare / maxFare) * 100)) : 0,
        target_column: this.detail?._model_meta?.[item.model_id]?.target_column || '',
      }))
    },
    prettyResult() {
      return this.detail?.result_json ? JSON.stringify(this.detail.result_json, null, 2) : '暂无结果文件'
    },
  },
  async mounted() {
    await this.refresh()
  },
  methods: {
    async refresh() {
      const res = await api.get('/predictions/')
      this.tasksAll = res.data
      this.tasks = this.tasksAll
    },
    async openDetail(row) {
      const res = await api.get(`/predictions/${row.id}/`)
      this.detail = res.data
      // fetch model meta for each model id to show target_column
      const ids = (this.detail.models_used || []).slice(0, 20)
      this.detail._model_meta = this.detail._model_meta || {}
      try {
        await Promise.all(ids.map(async (id) => {
          const r = await api.get(`/models/${id}/`)
          this.detail._model_meta[id] = { target_column: r.data.target_column || '' }
        }))
      } catch (e) {
        // ignore per-model fetch failures
      }
      this.detailVisible = true
    },
    async removeTask(row) {
      await this.$confirm(`确认删除任务「${row.name}」吗？`, '删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      })
      await api.delete(`/predictions/${row.id}/`)
      this.$message.success('任务已删除')
      await this.refresh()
    },
    applyLocalFilter() {
      const q = (this.searchQuery || '').toLowerCase()
      this.tasks = this.tasksAll.filter((t) => {
        if (this.statusFilter && t.status !== this.statusFilter) return false
        if (q && !(t.name || '').toLowerCase().includes(q)) return false
        return true
      })
    },
    downloadResult() {
      if (!this.detail?.result_json) return
      const data = JSON.stringify(this.detail.result_json, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `prediction_${this.detail.id}_result.json`
      a.click()
      URL.revokeObjectURL(url)
    },
  },
}
</script>

<style scoped>
.compact-stat {
  padding: 14px;
}

.detail-metric {
  font-size: 26px;
  font-weight: 700;
  margin-top: 8px;
}

.comparison-chart {
  display: grid;
  gap: 12px;
}

.comparison-row {
  display: grid;
  gap: 8px;
}

.comparison-label,
.comparison-values {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.comparison-bar-track {
  width: 100%;
  height: 14px;
  background: rgba(15, 118, 110, 0.10);
  border-radius: 999px;
  overflow: hidden;
}

.comparison-bar {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), #36c2b5);
}

.delta-up {
  color: var(--success);
  font-weight: 600;
}

.delta-down {
  color: var(--danger);
  font-weight: 600;
}

.detail-pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
}
</style>
