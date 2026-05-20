import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/AppLayout.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/HomeView.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'datasets',
          name: 'datasets',
          component: () => import('../views/DatasetView.vue'),
          meta: { title: '数据集管理' },
        },
        {
          path: 'models',
          name: 'models',
          component: () => import('../views/ModelView.vue'),
          meta: { title: '模型管理' },
        },
        {
          path: 'predictions',
          name: 'predictions',
          component: () => import('../views/PredictionListView.vue'),
          meta: { title: '预测任务' },
        },
        {
          path: 'predictions/new',
          name: 'prediction-create',
          component: () => import('../views/PredictionCreateView.vue'),
          meta: { title: '新建预测' },
        },
        {
          path: 'predictions/:id',
          name: 'prediction-result',
          component: () => import('../views/PredictionResultView.vue'),
          meta: { title: '预测详情' },
          props: true,
        },
      ],
    },
  ],
})

router.beforeEach(async (to, from) => {
  const authStore = useAuthStore()
  await authStore.initializeAuth()

  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }

  if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    return '/'
  }
})

export default router