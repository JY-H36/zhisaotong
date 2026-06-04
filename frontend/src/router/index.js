import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import ChatView from '../views/ChatView.vue'
import AdminView from '../views/AdminView.vue'

const routes = [
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/chat', name: 'Chat', component: ChatView, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/:pathMatch(.*)*', redirect: '/chat' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  const role = localStorage.getItem('auth_role')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin && role !== 'admin') {
    next('/chat')
  } else if (to.path === '/login' && token) {
    next(role === 'admin' ? '/admin' : '/chat')
  } else {
    next()
  }
})

export default router
