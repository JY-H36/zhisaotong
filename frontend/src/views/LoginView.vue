<script setup>
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth.js'

const { login, register } = useAuth()

const isLogin = ref(true)
const username = ref('')
const password = ref('')
const selectedRole = ref('user')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  if (!username.value.trim() || !password.value.trim()) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    if (isLogin.value) {
      await login(username.value.trim(), password.value, selectedRole.value)
    } else {
      await register(username.value.trim(), password.value)
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="logo">🤖</span>
        <h1>智扫通</h1>
        <p>机器人智能客服系统</p>
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <h2>{{ isLogin ? '登录' : '注册' }}</h2>

        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </div>

        <div v-if="isLogin" class="form-group">
          <label>登录身份</label>
          <div class="role-selector">
            <button
              type="button"
              class="role-btn"
              :class="{ active: selectedRole === 'user' }"
              @click="selectedRole = 'user'"
            >
              👤 普通用户
            </button>
            <button
              type="button"
              class="role-btn"
              :class="{ active: selectedRole === 'admin' }"
              @click="selectedRole = 'admin'"
            >
              ⚙️ 管理员
            </button>
          </div>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? '请稍候...' : (isLogin ? '登 录' : '注 册') }}
        </button>

        <p class="toggle-link">
          {{ isLogin ? '还没有账号？' : '已有账号？' }}
          <a href="#" @click.prevent="toggleMode">
            {{ isLogin ? '立即注册' : '去登录' }}
          </a>
        </p>
      </form>

      <div class="login-footer">
        <p>普通用户：user1001~user1010 / 123456 ｜ 管理员：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 420px;
  overflow: hidden;
}

.login-header {
  text-align: center;
  padding: 36px 32px 20px;
  background: #f9fafb;
}

.login-header .logo {
  font-size: 48px;
}

.login-header h1 {
  margin: 8px 0 4px;
  font-size: 26px;
  color: #1f2937;
  font-weight: 700;
}

.login-header p {
  color: #9ca3af;
  font-size: 14px;
  margin: 0;
}

.login-form {
  padding: 28px 32px 24px;
}

.login-form h2 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #374151;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}

.form-group input:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.error-msg {
  color: #ef4444;
  font-size: 13px;
  margin: 0 0 12px;
}

.btn-submit {
  width: 100%;
  padding: 13px;
  background: #4f46e5;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  margin-top: 4px;
}

.btn-submit:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle-link {
  text-align: center;
  margin: 14px 0 0;
  font-size: 13px;
  color: #9ca3af;
}

.toggle-link a {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.toggle-link a:hover {
  text-decoration: underline;
}

.login-footer {
  padding: 14px 32px 18px;
  text-align: center;
  border-top: 1px solid #f3f4f6;
}

.login-footer p {
  font-size: 12px;
  color: #d1d5db;
  margin: 0;
}

.role-selector {
  display: flex;
  gap: 10px;
}

.role-btn {
  flex: 1;
  padding: 10px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.role-btn:hover {
  border-color: #4f46e5;
  color: #4f46e5;
}

.role-btn.active {
  border-color: #4f46e5;
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 600;
}
</style>
