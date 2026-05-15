<template>
  <div class="login-container">
    <div class="login-card">
        <div class="split">
          <aside class="info-panel">
            <h2 class="info-title">货运费率预测系统</h2>
            <p class="info-description">基于 Vue 3 的多模型运价预测平台，提供历史查询、模型预测与用户管理功能。</p>
          </aside>

          <section class="form-panel">
            <header class="card-header">
              <h1 class="title">欢迎登录</h1>
              <p class="subtitle">请输入您的账户信息以继续</p>
            </header>

            <main class="card-body">
              <form class="login-form" @submit.prevent="handleLogin">
                <div class="form-row">
                  <label for="email">邮箱</label>
                  <input id="email" type="email" v-model="loginForm.email" placeholder="请输入邮箱" />
                </div>

                <div class="form-row">
                  <label for="password">密码</label>
                  <input id="password" type="password" v-model="loginForm.password" placeholder="请输入密码" />
                </div>

                <div class="form-row">
                  <button type="submit" :disabled="authStore.isLoading" class="btn-primary">
                    <span v-if="!authStore.isLoading">登录</span>
                    <span v-else>登录中...</span>
                  </button>
                </div>
              </form>

              <div class="form-footer">
                <span>还没有账户?</span>
                <a class="link" @click.prevent="navigateToRegister">去注册</a>
              </div>

              <div v-if="localError" class="error-message">{{ localError }}</div>
              <div v-else-if="authStore.error" class="error-message">{{ authStore.error }}</div>
            </main>
          </section>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { LoginRequest } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = reactive<LoginRequest>({ email: '', password: '' })
const localError = ref<string | null>(null)

function validateEmail(value: string) {
  if (!value) return false
  return /^\S+@\S+\.\S+$/.test(value)
}

const handleLogin = async () => {
  localError.value = null
  if (!validateEmail(loginForm.email)) {
    localError.value = '请输入有效的邮箱'
    return
  }
  if (!loginForm.password || loginForm.password.length < 6) {
    localError.value = '密码长度至少为6位'
    return
  }

  try {
    await authStore.login(loginForm)
    router.push('/')
  } catch (err: any) {
    localError.value = err.response?.data?.detail || err.message || '登录失败'
  }
}

const navigateToRegister = () => router.push('/register')
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: none;
  margin: 0;
  height: 100vh;
  background: #fff;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
}

.card-header {
  padding: 36px 24px;
  text-align: center;
  border-bottom: 1px solid #eef2f6;
}

.title {
  margin: 0;
  font-size: 28px;
  color: #333;
}


.card-body {
  padding: 24px 20px 32px;
}

.split { display:flex; flex-direction:row; }
.info-panel { flex:1; background: linear-gradient(135deg,#4b6cb7 0%,#182848 100%); color: #fff; padding: 48px 32px; display:flex; flex-direction:column; justify-content:center; min-height:100vh; }
.info-title { margin:0 0 12px; font-size:24px; }
.info-description { margin:0; color:rgba(255,255,255,0.9); }
.form-panel { flex:1; background:#fff; min-height:100vh; }

.login-form { display:flex; flex-direction:column; gap:16px; max-width:520px; }
.form-row { display:flex; flex-direction:column; gap:8px; }

.form-row label {
  font-size: 14px;
  color: #666;
}

.form-row input {
  height: 36px;
  padding: 6px 10px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  font-size: 14px;
}

.btn-primary {
  height: 40px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary[disabled] {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 18px;
  font-size: 13px;
  color: #666;
}

.link {
  color: #409eff;
  cursor: pointer;
  margin-left: 6px;
}

.error-message {
  margin-top: 16px;
  color: #f56c6c;
}

@media (max-width: 900px) {
  .split { flex-direction: column; }
  .info-panel { padding: 36px 20px; text-align:center; min-height: auto; }
  .form-panel .card-header { text-align:center; }
  .login-card { margin: 0; }
  .login-form { max-width:100%; }
}
</style>
