<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  ElMessage.success('已登出')
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="home-page">
    <div class="home-container">
      <header class="navbar">
        <div class="nav-left">
          <div class="logo">
            <svg width="32" height="32" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" fill="#1890FF" />
              <path d="M24 32L30 38L40 26" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span class="logo-text">运价预测系统</span>
          </div>
        </div>
        <div class="nav-right">
          <el-button type="primary" plain @click="handleLogout">登出</el-button>
        </div>
      </header>

      <main class="main-content">
        <div class="profile-card">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span class="title">个人信息</span>
              </div>
            </template>

            <div class="profile-info" v-if="authStore.user">
              <div class="info-item">
                <span class="label">用户名:</span>
                <span class="value">{{ authStore.user.username }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱:</span>
                <span class="value">{{ authStore.user.email }}</span>
              </div>
              <div class="info-item">
                <span class="label">用户 ID:</span>
                <span class="value">{{ authStore.user.id }}</span>
              </div>
            </div>

            <template #footer>
              <div class="card-footer">
                <el-button type="primary" @click="handleLogout">登出账号</el-button>
              </div>
            </template>
          </el-card>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
:root {
  --bg: #faf9f7;
  --card: #ffffff;
  --text: #1a1a1a;
  --text-secondary: #666666;
  --accent: #5a4a42;
  --border: #ebe8e3;
  --surface-shadow: rgba(26, 26, 26, 0.06);
}

.home-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg);
}

.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background: var(--card);
  padding: 18px 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  box-shadow: 0 2px 8px rgba(26, 26, 26, 0.03);
}

.nav-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.nav-right {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 80px 40px;
}

.profile-card {
  width: 100%;
  max-width: 820px;
}

:deep(.box-card) {
  border-radius: 16px;
  box-shadow: 0 12px 40px var(--surface-shadow);
  border: 1px solid var(--border);
}

:deep(.el-card__header) {
  padding: 20px 28px;
  border-bottom: 1px solid var(--border);
  background: var(--card);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
}

.profile-info {
  padding: 24px 28px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: var(--text);
  width: 180px;
  font-size: 13px;
  letter-spacing: 0.2px;
}

.value {
  color: var(--text-secondary);
  flex: 1;
  word-break: break-all;
  font-size: 13px;
}

:deep(.el-card__footer) {
  padding: 20px 28px;
  border-top: 1px solid var(--border);
  background: var(--card);
  display: flex;
  justify-content: flex-end;
}

.card-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-button--primary) {
  background: var(--accent);
  color: white;
  border: none;
}

:deep(.el-button--primary:hover) {
  background: #4a3a32;
}

:deep(.el-button--primary[plain]) {
  background: transparent;
  color: var(--accent);
  border-color: transparent;
}

:deep(.el-button--primary[plain]:hover) {
  background: #f3f1ed;
}
</style>
