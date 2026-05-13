<template>
  <div class="content-wrap">
    <div class="toolbar-row">
      <div>
        <h2 class="section-title">个人数据</h2>
        <p class="section-subtitle">查看当前任务、模型和历史预测的整体状态。</p>
      </div>
      <el-button type="primary" plain @click="$router.push('/predict')">新建预测任务</el-button>
    </div>

    <div class="hero-grid">
      <el-card class="surface-card" style="grid-column: span 4;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge">进行中</div>
          <el-statistic :value="stats.runningTasks" title="任务进行中" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 4;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(194, 65, 12, 0.10); color: var(--accent-2);">已完成</div>
          <el-statistic :value="stats.completedTasks" title="已完成任务" />
        </div>
      </el-card>
      <el-card class="surface-card" style="grid-column: span 4;">
        <div class="stack" style="gap: 10px;">
          <div class="soft-badge" style="background: rgba(21, 128, 61, 0.10); color: var(--success);">模型总数</div>
          <el-statistic :value="stats.modelCount" title="模型数量" />
        </div>
      </el-card>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <el-card class="surface-card" shadow="never">
          <template #header>
            <div class="toolbar-row">
              <strong>最近模型</strong>
              <el-button text @click="$router.push('/models')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="models" class="responsive-table" empty-text="暂无模型记录">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="status" label="状态" width="120" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="surface-card" shadow="never">
          <template #header>
            <div class="toolbar-row">
              <strong>最近预测任务</strong>
              <el-button text @click="$router.push('/history')">查看历史</el-button>
            </div>
          </template>
          <el-table :data="tasks" class="responsive-table" empty-text="暂无任务记录">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="status" label="状态" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      models: [],
      tasks: [],
      stats: {
        runningTasks: 0,
        completedTasks: 0,
        modelCount: 0,
      },
    }
  },
  async mounted() {
    const [modelRes, taskRes] = await Promise.all([api.get('/models/'), api.get('/predictions/')])
    this.models = modelRes.data.slice(-4).reverse()
    this.tasks = taskRes.data.slice(-4).reverse()
    this.stats.modelCount = modelRes.data.length
    this.stats.runningTasks = taskRes.data.filter((item) => item.status === 'running').length
    this.stats.completedTasks = taskRes.data.filter((item) => item.status === 'completed').length
  },
}
</script>
