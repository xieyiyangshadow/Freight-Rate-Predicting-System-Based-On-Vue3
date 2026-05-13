import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import type { AuthState, UserInfo, LoginRequest, RegisterRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // ============ 状态 ============
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ============ 计算属性 ============
  // 判断用户是否已登录
  const isAuthenticated = computed(() => !!accessToken.value)

  // ============ 方法 ============

  /**
   * 用户登录
   */
  const login = async (credentials: LoginRequest) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.loginUser(credentials)

      // 保存 token 和用户信息
      user.value = response.user
      accessToken.value = response.tokens.access
      refreshToken.value = response.tokens.refresh

      // 保存到本地存储（持久化）
      localStorage.setItem('accessToken', response.tokens.access)
      localStorage.setItem('refreshToken', response.tokens.refresh)
      localStorage.setItem('user', JSON.stringify(response.user))

      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || '登录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户注册
   */
  const register = async (formData: RegisterRequest) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await authApi.registerUser(formData)

      // 注册成功后自动登录
      user.value = response.user
      accessToken.value = response.tokens.access
      refreshToken.value = response.tokens.refresh

      localStorage.setItem('accessToken', response.tokens.access)
      localStorage.setItem('refreshToken', response.tokens.refresh)
      localStorage.setItem('user', JSON.stringify(response.user))

      return response
    } catch (err: any) {
      error.value = err.response?.data || err.message || '注册失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户登出
   */
  const logout = () => {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    error.value = null

    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  /**
   * 初始化认证状态（从本地存储恢复）
   */
  const initializeAuth = () => {
    const storedUser = localStorage.getItem('user')
    const storedAccessToken = localStorage.getItem('accessToken')
    const storedRefreshToken = localStorage.getItem('refreshToken')

    if (storedUser && storedAccessToken) {
      user.value = JSON.parse(storedUser)
      accessToken.value = storedAccessToken
      refreshToken.value = storedRefreshToken
    }
  }

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    // 计算属性
    isAuthenticated,
    // 方法
    login,
    register,
    logout,
    initializeAuth,
  }
})
