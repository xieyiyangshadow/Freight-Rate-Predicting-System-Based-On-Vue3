<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loginForm = reactive({
  email: '',
  password: '',
})

const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const showPassword = ref(false)

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await authStore.login({
          email: loginForm.email,
          password: loginForm.password,
        })
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error: any) {
        ElMessage.error(authStore.error || '登录失败，请重试')
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleLogin()
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="form-wrapper">
        <div class="brand-block">
          <div class="logo">
            <svg width="56" height="56" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" fill="#5a4a42" />
              <path d="M24 32L30 38L40 26" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <div>
              <h1 class="logo-text">运价预测系统</h1>
              <p class="subtitle">企业级运价预测</p>
            </div>
          </div>
          <p class="brand-note">为全球货运企业提供精准的价格预测与分析。在任何设备上都能获得完美体验。</p>
        </div>

        <div class="form-area">
          <div class="form-header">
            <h2>欢迎登录</h2>
            <p class="small-sub">输入邮箱和密码以继续</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            size="large"
            class="login-form"
          >
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                placeholder="邮箱地址"
                prefix-icon="Message"
                clearable
                autocomplete="email"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="密码"
                prefix-icon="Lock"
                clearable
                @keypress="handleKeyPress"
                :suffix-icon="showPassword ? 'Hide' : 'View'"
                @click.suffix="showPassword = !showPassword"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="authStore.isLoading"
                @click="handleLogin"
                class="login-button"
              >
                {{ authStore.isLoading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <el-link type="primary" :underline="false">忘记密码？</el-link>
            <el-divider direction="vertical" />
            <el-link type="primary" :underline="false" @click="goToRegister">创建账号</el-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
  /* Premium SwissSpa palette: warm pearl + deep mocha + restrained elegance */
  --bg: #faf9f7;
  --card: #ffffff;
  --brand-bg: #ede8e1; /* warm taupe background for brand section */
  --text: #1a1a1a;
  --text-secondary: #666666;
  --accent: #5a4a42; /* deep mocha/taupe accent */
  --border: #ebe8e3;
  --surface-shadow: rgba(26, 26, 26, 0.06);
  --focus-shadow: rgba(90, 74, 66, 0.08);
}

.login-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 80px;
}

.login-container {
  width: 100%;
  max-width: 1400px;
  background: var(--card);
  border-radius: 16px;
  box-shadow: 0 12px 40px var(--surface-shadow);
  padding: 0;
  border: 1px solid var(--border);
  overflow: hidden;
}

.form-wrapper {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  align-items: stretch;
}

.brand-block {
  background: var(--brand-bg);
  padding: 70px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-right: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 40px;
}

.logo svg {
  flex-shrink: 0;
  filter: drop-shadow(0 2px 8px rgba(90, 74, 66, 0.08));
  width: 64px;
  height: 64px;
}

.logo-text {
  font-size: 26px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
  letter-spacing: -0.6px;
  line-height: 1.2;
}

.subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 12px 0 0 0;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.brand-note {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.8;
  max-width: 100%;
  font-weight: 400;
}

.form-area {
  padding: 64px 56px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  margin-bottom: 44px;
  text-align: left;
}

.form-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.small-sub {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
}

.login-form {
  margin-bottom: 0;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

:deep(.el-input__wrapper) {
  background-color: #fafaf8;
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 14px 16px;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #d9d6d1;
  background-color: #fcfbf9;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent);
  background-color: #fefdfb;
  box-shadow: 0 6px 20px var(--focus-shadow);
}

:deep(.el-input__inner) {
  font-size: 16px;
  color: var(--text);
  padding: 10px 8px;
  font-weight: 400;
}

:deep(.el-input__inner::placeholder) {
  color: #b8b3ad;
  font-weight: 400;
}

:deep(.el-input__prefix, .el-input__suffix) {
  color: #9a9490;
}

.login-button {
  width: 100%;
  height: 54px;
  font-size: 16px;
  font-weight: 600;
  background: var(--accent);
  color: #ffffff;
  border: none;
  margin-top: 12px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(90, 74, 66, 0.06);
  transition: all 0.2s ease;
  letter-spacing: 0.2px;
}

.login-button:hover {
  background: #4a3a32;
  box-shadow: 0 12px 32px rgba(90, 74, 66, 0.12);
  transform: translateY(-1px);
}

.login-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 16px rgba(90, 74, 66, 0.08);
}

.form-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 24px;
}

:deep(.el-link--primary) {
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
  transition: color 0.2s ease;
}

:deep(.el-link--primary:hover) {
  color: #6a5a52;
}

:deep(.el-divider--vertical) {
  margin: 0 8px;
  border-left-color: var(--border);
  height: 14px;
}
</style>
