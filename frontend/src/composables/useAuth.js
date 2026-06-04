import { ref } from 'vue'
import { useRouter } from 'vue-router'

/** 全局认证状态（单例） */
const user = ref(null)
const token = ref(localStorage.getItem('auth_token') || '')
const role = ref(localStorage.getItem('auth_role') || '')

export function useAuth() {
  const router = useRouter()

  /** 获取认证 header */
  function authHeaders() {
    return token.value ? { Authorization: `Bearer ${token.value}` } : {}
  }

  /** 是否为管理员 */
  function isAdmin() {
    return role.value === 'admin'
  }

  /** 登录 */
  async function login(username, password, selectedRole = 'user') {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role: selectedRole }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '登录失败')
    }
    const data = await res.json()
    token.value = data.token
    role.value = data.role
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('auth_role', data.role)
    user.value = { id: data.user_id, username: data.username, role: data.role }

    // 管理员跳转后台，普通用户跳转聊天
    if (data.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/chat')
    }
  }

  /** 注册 */
  async function register(username, password) {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || '注册失败')
    }
    const data = await res.json()
    token.value = data.token
    role.value = data.role
    localStorage.setItem('auth_token', data.token)
    localStorage.setItem('auth_role', data.role)
    user.value = { id: data.user_id, username: data.username, role: data.role }
    router.push('/chat')
  }

  /** 初始化时从服务端恢复用户信息 */
  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await fetch('/api/auth/me', {
        headers: authHeaders(),
      })
      if (res.ok) {
        user.value = await res.json()
        role.value = user.value.role || 'user'
      } else {
        logout()
      }
    } catch {
      // 网络错误，保持当前状态
    }
  }

  /** 登出 */
  function logout() {
    token.value = ''
    role.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_role')
    router.push('/login')
  }

  return { user, token, role, authHeaders, isAdmin, login, register, fetchMe, logout }
}
