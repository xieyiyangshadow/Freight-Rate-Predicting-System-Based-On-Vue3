<template>
  <div class="auth-shell">
    <section class="auth-hero">
      <div class="auth-copy">
        <div class="soft-badge">登录入口</div>
        <h1>让运价预测流程真正可用。</h1>
        <p>通过电话号码和密码登录后，即可进入统一仪表盘，管理模型训练、查看历史任务并创建新的预测请求。</p>
      </div>
    </section>

    <section class="auth-panel">
      <el-card class="glass-panel auth-card" shadow="never">
        <div class="stack">
          <div>
            <h2 class="section-title">登录</h2>
            <p class="section-subtitle">使用电话号码和密码进入系统。</p>
          </div>
          <el-form label-position="top" @submit.prevent="submit">
            <el-form-item 
              label="电话号码" 
              :error="errors.phone"
            >
              <el-input 
                v-model="form.phone" 
                placeholder="请输入电话号码" 
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
                placeholder="请输入密码" 
                size="large" 
                show-password
                @input="clearError('password')"
              />
            </el-form-item>
            <div class="auth-actions">
              <el-button type="primary" size="large" :loading="loading" @click="submit">登录</el-button>
              <el-button text @click="$router.push('/register')">没有账号？去注册</el-button>
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
      form: { phone: '', password: '' },
      errors: {
        phone: '',
        password: '',
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
      this.errors.phone = ''
      this.errors.password = ''
      this.globalError = ''

      let isValid = true

      // 电话号码验证
      if (!this.form.phone || !this.form.phone.trim()) {
        this.errors.phone = '请输入电话号码'
        isValid = false
      }

      // 密码验证
      if (!this.form.password) {
        this.errors.password = '请输入密码'
        isValid = false
      }

      return isValid
    },
    async submit() {
      if (!this.validateForm()) {
        this.$message.warning('请填写完整信息')
        return
      }

      this.loading = true
      try {
        const res = await api.post('/users/login/', this.form)
        setCurrentUser(res.data)
        this.$message.success('登录成功')
        this.$router.push('/')
      } catch (error) {
        const detail = error?.response?.data?.detail
        this.globalError = detail || error?.message || '登录失败，请重试'
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
