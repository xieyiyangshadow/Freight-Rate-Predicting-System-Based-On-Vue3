import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
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
      path: '/datasets',
      name: 'datasets',
      component: () => import('../views/DatasetView.vue'),
      meta: { requiresAuth: true },
    },
    // {
    //   path: '/models',
    //   name: 'models',
    //   component: () => import('../views/ModelView.vue'),
    //   meta: { requiresAuth: true },
    // },
    // {
    //   path: '/predictions',
    //   name: 'predictions',
    //   component: () => import('../views/PredictionListView.vue'),
    //   meta: { requiresAuth: true },
    // },
    // {
    //   path: '/predictions/new',
    //   name: 'prediction-create',
    //   component: () => import('../views/PredictionCreateView.vue'),
    //   meta: { requiresAuth: true },
    // },
    // {
    //   path: '/predictions/:id',
    //   name: 'prediction-result',
    //   component: () => import('../views/PredictionResultView.vue'),
    //   meta: { requiresAuth: true },
    //   props: true,
    // },
  ], 
}) 

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.initializeAuth()

  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router