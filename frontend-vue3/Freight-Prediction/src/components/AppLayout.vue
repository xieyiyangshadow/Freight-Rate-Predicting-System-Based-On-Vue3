<script setup lang="ts">
import { computed, watch, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navItems = [
  { label: '首页', to: '/', hint: '总览与快捷入口' },
  { label: '数据集', to: '/datasets', hint: '上传与查看数据资产' },
  { label: '模型', to: '/models', hint: '训练状态与模型详情' },
  { label: '预测任务', to: '/predictions', hint: '任务列表与结果追踪' },
  { label: '新建预测', to: '/predictions/new', hint: '快速发起一次预测' },
]

const currentTitle = computed(() => {
  const matched = route.matched[route.matched.length - 1]
  return (matched?.meta?.title as string) || '控制台'
})

const currentDescription = computed(() => {
  const descriptions: Record<string, string> = {
    '/': '主页概览、快捷入口和账户信息。',
    '/datasets': '管理训练所需的数据集并查看字段结构。',
    '/models': '追踪模型训练进度、失败项和详细指标。',
    '/predictions': '监控预测任务的执行状态与结果。',
    '/predictions/new': '创建新的预测任务并选择可用模型。',
  }

  return descriptions[route.path] || '统一的业务工作台。'
})

const userLabel = computed(() => authStore.user?.username || authStore.user?.email || '未命名用户')

const handleLogout = () => {
  if (!window.confirm('确定要退出登录吗？')) {
    return
  }

  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  console.log('[AppLayout] mounted, route=', route.fullPath)
})

watch(
  () => route.fullPath,
  (v, o) => {
    console.log('[AppLayout] route change', { from: o, to: v })
  },
)
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand-block">
        <div class="brand-mark">F</div>
        <div>
          <h1>货运费率预测</h1>
          <p>多模型运价预测控制台</p>
        </div>
      </div>

      <nav class="nav-list" aria-label="主导航">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          exact-active-class="is-active"
        >
          <span class="nav-title">{{ item.label }}</span>
          <span class="nav-hint">{{ item.hint }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-card">
          <span class="user-label">当前登录</span>
          <strong>{{ userLabel }}</strong>
          <small v-if="authStore.user?.email">{{ authStore.user.email }}</small>
        </div>
        <button class="logout-button" type="button" @click="handleLogout">退出登录</button>
      </div>
    </aside>

    <section class="content-shell">
      <header class="topbar">
        <div>
          <p class="page-kicker">{{ currentTitle }}</p>
          <h2>{{ currentDescription }}</h2>
        </div>
        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
          <div class="status-chip">已登录</div>
          <small style="color:#6b7d97;">route: {{ route.path }}</small>
        </div>
      </header>

      <main class="page-body">
        <RouterView v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component v-if="Component" :is="Component" :key="route.fullPath" />
          </transition>
        </RouterView>
      </main>
    </section>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 292px minmax(0, 1fr);
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(60, 110, 255, 0.18), transparent 32%),
    linear-gradient(180deg, #f5f8ff 0%, #eef3fb 100%);
  color: #122033;
  font-family: 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 28px 20px;
  background: rgba(10, 18, 36, 0.92);
  color: #f4f7fb;
  backdrop-filter: blur(14px);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 10px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #58a6ff 0%, #7c5cff 100%);
  color: #fff;
  font-weight: 700;
  font-size: 22px;
}

.brand-block h1 {
  margin: 0;
  font-size: 18px;
}

.brand-block p {
  margin: 4px 0 0;
  color: rgba(244, 247, 251, 0.72);
  font-size: 13px;
}

.nav-list {
  display: grid;
  gap: 10px;
}

.nav-item {
  display: grid;
  gap: 4px;
  padding: 14px 16px;
  border-radius: 16px;
  color: #d7deea;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid transparent;
  transition: 0.2s ease;
}

.nav-item:hover,
.nav-item.is-active {
  color: #ffffff;
  background: rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.28);
  transform: translateX(2px);
}

.nav-title {
  font-size: 15px;
  font-weight: 600;
}

.nav-hint {
  font-size: 12px;
  color: inherit;
  opacity: 0.78;
}

.sidebar-footer {
  margin-top: auto;
  display: grid;
  gap: 12px;
}

.user-card {
  display: grid;
  gap: 4px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.05);
}

.user-label {
  font-size: 12px;
  color: rgba(244, 247, 251, 0.7);
}

.user-card strong {
  font-size: 15px;
}

.user-card small {
  color: rgba(244, 247, 251, 0.7);
  word-break: break-all;
}

.logout-button {
  border: 0;
  border-radius: 14px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #ff7b72 0%, #ff5f6d 100%);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.content-shell {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-width: 0;
}

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  padding: 28px 32px 14px;
}

.page-kicker {
  margin: 0 0 8px;
  color: #54709a;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.topbar h2 {
  margin: 0;
  max-width: 820px;
  font-size: 24px;
  line-height: 1.35;
  color: #142033;
}

.status-chip {
  flex: none;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(64, 158, 255, 0.12);
  color: #286bc3;
  font-size: 13px;
  font-weight: 600;
}

.page-body {
  min-width: 0;
  padding: 0 32px 32px;
  overflow: auto;
}

@media (max-width: 1024px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: sticky;
    top: 0;
    z-index: 20;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .page-body,
  .topbar {
    padding-left: 20px;
    padding-right: 20px;
  }
}

@media (max-width: 720px) {
  .topbar {
    flex-direction: column;
  }
}
</style>
