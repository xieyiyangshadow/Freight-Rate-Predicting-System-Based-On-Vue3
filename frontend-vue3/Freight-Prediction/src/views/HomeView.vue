<template>
  <div class="home-container">
    <div class="home-card">
      <header class="card-header">
        <h1 class="title">欢迎回来</h1>
      </header>

      <main class="card-body">
        <section v-if="authStore.user" class="user-info">
          <div class="info-row"><strong>用户ID：</strong><span>{{ authStore.user.id }}</span></div>
          <div class="info-row"><strong>用户名：</strong><span>{{ authStore.user.username }}</span></div>
          <div class="info-row"><strong>邮箱：</strong><span>{{ authStore.user.email }}</span></div>

          <div class="logout-button">
            <button class="btn-danger" @click="handleLogout">退出登录</button>
          </div>
        </section>

        <section v-else class="no-user">
          <p>未加载用户信息</p>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  if (window.confirm('确定要退出登录吗？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.home-container { display:flex; justify-content:center; align-items:center; width:100%; height:100vh; background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); }
.home-card { width:100%; max-width:none; margin:0; height:100vh; background:#fff; border-radius:0; box-shadow:none; overflow:hidden; }
.card-header { padding:36px 24px; text-align:center; border-bottom:1px solid #eef2f6; }
.title { margin:0; font-size:28px; color:#333; }
.card-body { padding:32px 40px 48px; }
.user-info { display:flex; flex-direction:column; gap:12px; align-items:flex-start; }
.info-row { font-size:16px; color:#333; }
.logout-button { margin-top:24px; }
.btn-danger { background:#f56c6c; color:#fff; border:none; padding:10px 18px; border-radius:6px; cursor:pointer; }
.no-user { padding:40px; text-align:center; color:#666; }
</style>

