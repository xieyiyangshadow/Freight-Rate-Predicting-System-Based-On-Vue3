<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref()
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: '',
})

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符之间', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少 8 个字符', trigger: 'blur' },
  ],
  password2: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少 8 个字符', trigger: 'blur' },
  ],
}

const showPassword = ref(false)
const showConfirmPassword = ref(false)

// 计算密码强度
const passwordStrength = computed(() => {
  const pwd = registerForm.password
  if (!pwd) return 0

  let strength = 0
  if (pwd.length >= 8) strength += 20
  if (pwd.length >= 12) strength += 10
  if (/[a-z]/.test(pwd)) strength += 20
  if (/[A-Z]/.test(pwd)) strength += 20
  if (/[0-9]/.test(pwd)) strength += 15
  if (/[^a-zA-Z0-9]/.test(pwd)) strength += 15

  return Math.min(strength, 100)
})

const passwordStrengthText = computed(() => {
  if (passwordStrength.value < 40) return '弱'
  if (passwordStrength.value < 70) return '中'
  return '强'
})

const passwordStrengthColor = computed(() => {
  if (passwordStrength.value < 40) return '#f56c6c'
  if (passwordStrength.value < 70) return '#e6a23c'
  return '#67c23a'
})

// 密码需求检查
const passwordRequirements = computed(() => ({
  length: registerForm.password.length >= 8,
  hasCase: /[a-z]/.test(registerForm.password) && /[A-Z]/.test(registerForm.password),
  hasNumber: /[0-9]/.test(registerForm.password),
  matches: registerForm.password === registerForm.password2 && registerForm.password2 !== '',
}))

const handleRegister = async () => {
  if (!registerFormRef.value) return

  // 验证两次密码是否一致
  if (registerForm.password !== registerForm.password2) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  await registerFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await authStore.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          password2: registerForm.password2,
        })
        ElMessage.success('注册成功')
        router.push('/')
      } catch (error: any) {
        ElMessage.error(authStore.error || '注册失败，请重试')
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}

const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleRegister()
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <div class="form-wrapper">
        <div class="form-header">
          <div class="logo">
            <svg width="40" height="40" viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="30" fill="#5a4a42" />
              <path d="M24 32L30 38L40 26" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <h1 class="logo-text">运价预测系统</h1>
          </div>
          <p class="subtitle">创建一个账户以使用运价预测服务</p>
        </div>

        <el-form
          ref="registerFormRef"
          :model="registerForm"
          :rules="registerRules"
          size="large"
          class="register-form"
        >
          <el-form-item prop="username">
            <el-input v-model="registerForm.username" placeholder="用户名 (3-20 字符)" prefix-icon="User" clearable />
          </el-form-item>

          <el-form-item prop="email">
            <el-input v-model="registerForm.email" placeholder="邮箱地址" prefix-icon="Message" clearable />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="registerForm.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码 (至少 8 个字符)"
              prefix-icon="Lock"
              clearable
              :suffix-icon="showPassword ? 'Hide' : 'View'"
              @click.suffix="showPassword = !showPassword"
            />

            <div class="strength-indicator">
              <div class="strength-bar">
                <div
                  class="strength-fill"
                  :style="{ width: passwordStrength + '%', backgroundColor: passwordStrengthColor }"
                />
              </div>
              <span class="strength-text">强度: {{ passwordStrengthText }}</span>
            </div>

            <div class="password-requirements">
              <div :class="{ 'requirement-item': true, 'met': passwordRequirements.length }">
                <el-icon><component :is="passwordRequirements.length ? 'Check' : 'Close'" /></el-icon>
                <span>至少 8 个字符</span>
              </div>
              <div :class="{ 'requirement-item': true, 'met': passwordRequirements.hasCase }">
                <el-icon><component :is="passwordRequirements.hasCase ? 'Check' : 'Close'" /></el-icon>
                <span>包含大小写字母</span>
              </div>
              <div :class="{ 'requirement-item': true, 'met': passwordRequirements.hasNumber }">
                <el-icon><component :is="passwordRequirements.hasNumber ? 'Check' : 'Close'" /></el-icon>
                <span>包含数字</span>
              </div>
            </div>
          </el-form-item>

          <el-form-item prop="password2">
            <el-input
              v-model="registerForm.password2"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="确认密码"
              prefix-icon="Lock"
              clearable
              :suffix-icon="showConfirmPassword ? 'Hide' : 'View'"
              @click.suffix="showConfirmPassword = !showConfirmPassword"
              @keypress="handleKeyPress"
            />
            <div v-if="registerForm.password2" :class="{ 'match-indicator': true, 'matched': passwordRequirements.matches }">
              <el-icon><component :is="passwordRequirements.matches ? 'Check' : 'Close'" /></el-icon>
              <span>{{ passwordRequirements.matches ? '密码一致' : '密码不一致' }}</span>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" :loading="authStore.isLoading" @click="handleRegister" class="register-button">
              {{ authStore.isLoading ? '注册中...' : '注册账号' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="form-footer">
          <p class="login-prompt">已有账号？<el-link type="primary" :underline="false" @click="goToLogin">立即登录</el-link></p>
        </div>
      </div>
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
  --focus-shadow: rgba(90, 74, 66, 0.08);
}

.register-page {
  width: 100%;
  min-height: 100vh;
  background: var(--bg);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 40px;
}

.register-container {
  width: 100%;
  max-width: 600px;
  background: var(--card);
  border-radius: 16px;
  box-shadow: 0 12px 40px var(--surface-shadow);
  padding: 56px;
  border: 1px solid var(--border);
}

.form-wrapper { width: 100%; }

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  margin-bottom: 12px;
}

.logo svg {
  filter: drop-shadow(0 2px 8px rgba(90, 74, 66, 0.08));
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
  letter-spacing: -0.3px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 4px;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-input__wrapper) {
  background: #fafaf8;
  border-radius: 8px;
  border: 1px solid var(--border);
  padding: 10px 12px;
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
  font-size: 14px;
  color: var(--text);
  padding: 6px 4px;
}

:deep(.el-input__inner::placeholder) {
  color: #b8b3ad;
}

.strength-indicator {
  margin-top: 10px;
  margin-bottom: 10px;
}

.strength-bar {
  height: 6px;
  background: #ebe8e3;
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease, background-color 0.3s;
}

.strength-text {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-weight: 500;
}

.password-requirements {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #b8b3ad;
  font-size: 12px;
  font-weight: 400;
}

.requirement-item.met {
  color: var(--accent);
}

.match-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #d9534f;
  margin-top: 8px;
  font-size: 12px;
}

.match-indicator.matched {
  color: var(--accent);
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 14px;
  font-weight: 600;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(90, 74, 66, 0.06);
  transition: all 0.2s ease;
  margin-top: 12px;
  letter-spacing: 0.2px;
}

.register-button:hover {
  background: #4a3a32;
  box-shadow: 0 12px 32px rgba(90, 74, 66, 0.12);
  transform: translateY(-1px);
}

.register-button:active {
  transform: translateY(0);
  box-shadow: 0 4px 16px rgba(90, 74, 66, 0.08);
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.login-prompt {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

:deep(.el-link--primary) {
  font-size: 12px;
  color: var(--accent);
  margin-left: 4px;
  font-weight: 500;
}

:deep(.el-link--primary:hover) {
  color: #6a5a52;
}
</style>
