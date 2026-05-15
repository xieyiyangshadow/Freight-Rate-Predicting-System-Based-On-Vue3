<template>
	<div class="register-container">
		<div class="register-card">
			<div class="split">
				<aside class="info-panel">
					<h2 class="info-title">开始您的预测之旅</h2>
					<p class="info-description">快速注册账号，访问历史记录、模型预测和个性化设置。</p>
				</aside>

				<section class="form-panel">
					<header class="card-header">
						<h1 class="title">注册</h1>
						<p class="subtitle">创建新账号以继续</p>
					</header>

					<main class="card-body">
						<form class="register-form" @submit.prevent="handleRegister">
							<div class="form-row">
								<label for="username">用户名</label>
								<input id="username" v-model="registerForm.username" placeholder="请输入用户名" />
							</div>

							<div class="form-row">
								<label for="email">邮箱</label>
								<input id="email" type="email" v-model="registerForm.email" placeholder="请输入邮箱" />
							</div>

							<div class="form-row">
								<label for="password">密码</label>
								<input id="password" type="password" v-model="registerForm.password" placeholder="请输入密码" />
							</div>

							<div class="form-row">
								<label for="password2">确认密码</label>
								<input id="password2" type="password" v-model="registerForm.password2" placeholder="请再次输入密码" />
							</div>

							<div class="form-row">
								<button type="submit" :disabled="authStore.isLoading" class="btn-primary">注册</button>
							</div>
						</form>

						<div class="form-footer">
							<span>已有账户?</span>
							<a class="link" @click.prevent="navigateToLogin">去登录</a>
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
import type { RegisterRequest } from '@/types/auth'

const router = useRouter()
const authStore = useAuthStore()

const registerForm = reactive<RegisterRequest>({ username: '', email: '', password: '', password2: '' })
const localError = ref<string | null>(null)

function validateEmail(value: string) {
	if (!value) return false
	return /^\S+@\S+\.\S+$/.test(value)
}

const handleRegister = async () => {
	localError.value = null
	if (!registerForm.username || registerForm.username.length < 3) {
		localError.value = '用户名长度至少为3位'
		return
	}
	if (!validateEmail(registerForm.email)) {
		localError.value = '请输入有效的邮箱'
		return
	}
	if (!registerForm.password || registerForm.password.length < 6) {
		localError.value = '密码长度至少为6位'
		return
	}
	if (registerForm.password !== registerForm.password2) {
		localError.value = '两次输入的密码不一致'
		return
	}

	try {
		await authStore.register(registerForm)
		router.push('/')
	} catch (err: any) {
		localError.value = err.response?.data || err.message || '注册失败'
	}
}

const navigateToLogin = () => router.push('/login')
</script>

<style scoped>
.register-container {
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
	height: 100vh;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
	width: 100%;
	max-width: none;
	margin: 0;
	height: 100vh;
	background: #fff;
	border-radius: 0;
	overflow: hidden;
	box-shadow: none;
}

.card-header { padding: 20px 24px; text-align: left; border-bottom: 1px solid #eef2f6; }
.title { margin: 0; font-size: 22px; color: #333; }
.subtitle { margin:4px 0 0; color:#666; }
.card-body { padding: 24px 20px 32px; }
.split { display:flex; }
.info-panel { flex:1; background: linear-gradient(135deg,#4b6cb7 0%,#182848 100%); color:#fff; padding:48px 32px; display:flex; flex-direction:column; justify-content:center; min-height:100vh; }
.info-title { margin:0 0 12px; font-size:20px; }
.info-description { margin:0; color:rgba(255,255,255,0.9); }
.form-panel { flex:1; background:#fff; min-height:100vh; }
.register-form { display:flex; flex-direction:column; gap:16px; max-width:520px; }
.form-row { display:flex; flex-direction:column; gap:8px; }
.form-row label { font-size:14px; color:#666; }
.form-row input { height:36px; padding:6px 10px; border:1px solid #e6e6e6; border-radius:4px; font-size:14px; }
.btn-primary { height:40px; background:#409eff; color:#fff; border:none; border-radius:4px; cursor:pointer; }
.btn-primary[disabled]{ opacity:0.7; cursor:not-allowed; }
.form-footer { margin-top:18px; font-size:13px; color:#666; }
.link { color:#409eff; cursor:pointer; margin-left:6px; }
.error-message { margin-top:16px; color:#f56c6c; }

@media (max-width:900px) {
	.split { flex-direction: column; }
	.info-panel { padding: 36px 20px; text-align:center; min-height:auto; }
	.form-panel .card-header { text-align:center; }
	.register-card { margin: 0; }
	.register-form { max-width:100%; }
}
</style>
