<template>
  <div class="auth-shell">
    <section class="auth-hero">
      <div class="auth-copy">
        <div class="soft-badge">创建账户</div>
        <h1>注册后自动登录，立刻进入系统。</h1>
        <p>注册时需要用户名、电话号码和密码。电话号码已存在时，系统会明确提示并阻止重复注册。</p>
      </div>
    </section>

    <section class="auth-panel">
      <el-card class="glass-panel auth-card" shadow="never">
        <div class="stack">
          <div>
            <h2 class="section-title">注册</h2>
            <p class="section-subtitle">输入用户名、电话号码和密码。</p>
          </div>
          <el-form ref="formRef" :model="form" label-position="top" @submit.prevent="submit">
            <el-form-item 
              label="用户名" 
              :error="errors.username"
            >
              <el-input 
                v-model="form.username" 
                placeholder="请输入用户名（至少2个字符）" 
                size="large"
                clearable
                @input="clearError('username')"
              />
            </el-form-item>
            <el-form-item 
              label="电话号码" 
              :error="errors.phone"
            >
              <el-input 
                v-model="form.phone" 
                placeholder="请输入电话号码（至少5个数字）" 
                size="large"
                clearable
                @input="clearError('phone')"
              />
            </el-form-item>
            <el-form-item 
              label="密码" 
              :error="errors.password"
            >
              <el-input 
                v-model="form.password" 
                type="password" 
                placeholder="请输入密码（至少6个字符）" 
                size="large" 
                show-password
                @input="clearError('password')"
              />
            </el-form-item>
            <el-form-item 
              label="确认密码" 
              :error="errors.password_confirm"
            >
              <el-input 
                v-model="form.password_confirm" 
                type="password" 
                placeholder="再次输入密码" 
                size="large" 
                show-password
                @input="clearError('password_confirm')"
              />
            </el-form-item>
            <div class="auth-actions">
              <el-button type="primary" size="large" :loading="loading" @click="submit">注册并登录</el-button>
              <el-button text @click="$router.push('/login')">已有账号？去登录</el-button>
            </div>
          </el-form>
          <div v-if="globalError" class="error-box">
            <p>{{ globalError }}</p>
          </div>
        </div>
      </el-card>
    </section>
  </div>
</template>

<script>
import api, { setCurrentUser } from '../api'

export default {
  data() {
    return {
      loading: false,
      form: { username: '', phone: '', password: '', password_confirm: '' },
      errors: {
        username: '',
        phone: '',
        password: '',
        password_confirm: '',
      },
      globalError: '',
    }
  },
  methods: {
    clearError(field) {
      this.errors[field] = ''
      this.globalError = ''
    },
    validateForm() {
      // 清除所有错误
      Object.keys(this.errors).forEach(key => this.errors[key] = '')
      this.globalError = ''

      let isValid = true

      // 用户名验证
      if (!this.form.username || !this.form.username.trim()) {
        this.errors.username = '用户名不能为空'
        isValid = false
      } else if (this.form.username.length < 2) {
        this.errors.username = '用户名至少2个字符'
        isValid = false
      } else if (this.form.username.length > 150) {
        this.errors.username = '用户名最多150个字符'
        isValid = false
      }

      // 电话号码验证
      if (!this.form.phone || !this.form.phone.trim()) {
        this.errors.phone = '电话号码不能为空'
        isValid = false
      } else if (!/\d{5,}/.test(this.form.phone)) {
        this.errors.phone = '电话号码格式不正确（至少包含5个数字）'
        isValid = false
      }

      // 密码验证
      if (!this.form.password) {
        this.errors.password = '密码不能为空'
        isValid = false
      } else if (this.form.password.length < 6) {
        this.errors.password = '密码至少6个字符'
        isValid = false
      }

      // 确认密码验证
      if (!this.form.password_confirm) {
        this.errors.password_confirm = '请确认密码'
        isValid = false
      } else if (this.form.password !== this.form.password_confirm) {
        this.errors.password_confirm = '两次输入的密码不一致'
        isValid = false
      }

      return isValid
    },
    async submit() {
      if (!this.validateForm()) {
        this.$message.warning('请检查表单信息')
        return
      }

      this.loading = true
      try {
        const payload = {
          username: this.form.username,
          phone: this.form.phone,
          password: this.form.password,
        }
        const res = await api.post('/users/register/', payload)
        setCurrentUser(res.data)
        this.$message.success('注册成功并已自动登录')
        this.$router.push('/')
      } catch (error) {
        // 处理服务器返回的错误
        const detail = error?.response?.data?.detail
        if (detail) {
          // 如果返回的是字段级错误（包含 |），分开显示
          if (typeof detail === 'string' && detail.includes('|')) {
            this.globalError = detail
          } else {
            this.globalError = detail
          }
        } else if (error?.response?.data) {
          // 处理其他结构的错误响应
          const errorData = error.response.data
          if (typeof errorData === 'object') {
            const messages = []
            for (const [key, value] of Object.entries(errorData)) {
              if (Array.isArray(value)) {
                messages.push(value[0])
              } else if (typeof value === 'string') {
                messages.push(value)
              }
            }
            this.globalError = messages.join(' | ') || '注册失败'
          } else {
            this.globalError = '注册失败'
          }
        } else {
          this.globalError = error?.message || '网络错误，请重试'
        }
        this.$message.error(this.globalError)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.error-box {
  margin-top: 16px;
  padding: 12px;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 4px;
  color: #c33;
  font-size: 14px;
}
</style>
