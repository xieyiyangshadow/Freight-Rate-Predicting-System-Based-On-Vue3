import { createRouter, createWebHistory } from 'vue-router'
import Login from './pages/Login.vue'
import Register from './pages/Register.vue'
import Dashboard from './pages/Dashboard.vue'
import Models from './pages/Models.vue'
import Predict from './pages/Predict.vue'
import History from './pages/History.vue'
import Datasets from './pages/Datasets.vue'
import { getCurrentUser } from './api'

const routes = [
  { path: '/', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },
  { path: '/models', component: Models, meta: { requiresAuth: true } },
  { path: '/datasets', component: Datasets, meta: { requiresAuth: true } },
  { path: '/predict', component: Predict, meta: { requiresAuth: true } },
  { path: '/history', component: History, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const user = getCurrentUser()
  if (to.meta.requiresAuth && !user) {
    return '/login'
  }
  if (to.meta.public && user) {
    return '/'
  }
  return true
})

export default router
