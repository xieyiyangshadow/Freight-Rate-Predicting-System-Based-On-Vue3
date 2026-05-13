<template>
  <router-view v-if="isAuthRoute" />
  <div v-else class="page-shell app-grid">
    <aside class="app-sidebar">
      <div class="glass-panel sidebar-card">
        <div class="sidebar-brand">
          <div class="soft-badge">Freight Intelligence</div>
          <h1>多模型运价预测系统</h1>
          <p>统一管理用户、训练模型、运价预测任务与历史记录，所有页面保持一致的视觉语言。</p>
        </div>

        <el-menu class="surface-card" router :default-active="$route.path">
          <el-menu-item index="/">个人数据</el-menu-item>
          <el-menu-item index="/models">预测模型</el-menu-item>
            <el-menu-item index="/datasets">数据集</el-menu-item>
          <el-menu-item index="/predict">运价预测</el-menu-item>
          <el-menu-item index="/history">历史预测</el-menu-item>
        </el-menu>

        <div class="sidebar-actions">
          <el-card shadow="never" class="surface-card">
            <div class="stack" style="gap: 8px;">
              <div class="muted-text">当前用户</div>
              <strong>{{ currentUser?.username || '未登录' }}</strong>
              <div class="muted-text">{{ currentUser?.phone || '请先登录后使用全部功能' }}</div>
            </div>
          </el-card>
          <template v-if="!currentUser">
            <el-button type="primary" plain @click="goAuth('/login')">登录</el-button>
            <el-button @click="goAuth('/register')">注册</el-button>
          </template>
          <el-button v-else type="danger" plain @click="logout">退出登录</el-button>
        </div>
      </div>
    </aside>

    <main class="main-panel">
      <section class="glass-panel main-card">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script>
import { getCurrentUser, clearCurrentUser } from './api'

export default {
  name: 'App',
  data() {
    return {
      userSnapshot: getCurrentUser(),
    }
  },
  computed: {
    currentUser() {
      return this.userSnapshot
    },
    isAuthRoute() {
      return ['/login', '/register'].includes(this.$route.path)
    },
  },
  mounted() {
    window.addEventListener('freight-auth-changed', this.syncUser)
  },
  beforeUnmount() {
    window.removeEventListener('freight-auth-changed', this.syncUser)
  },
  methods: {
    syncUser(event) {
      this.userSnapshot = event?.detail || getCurrentUser()
    },
    goAuth(path) {
      this.$router.push(path)
    },
    logout() {
      clearCurrentUser()
      this.$router.push('/login')
    },
  },
}
</script>