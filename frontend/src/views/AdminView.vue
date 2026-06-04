<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth.js'

const { user, authHeaders, logout } = useAuth()

const activeTab = ref('users')
const stats = ref({})
const users = ref([])
const selectedUserChats = ref([])
const knowledgeFiles = ref([])
const dataPath = ref('')
const loading = ref(false)
const uploadMsg = ref('')
const uploadMsgOk = ref(true)
const viewingFile = ref(null)
const fileContent = ref('')
const fileContentType = ref('')

// ==================== 加载数据 ====================

async function loadStats() {
  const res = await fetch('/api/admin/stats', { headers: authHeaders() })
  if (res.ok) stats.value = await res.json()
}

async function loadUsers() {
  const res = await fetch('/api/admin/users', { headers: authHeaders() })
  if (res.ok) {
    const data = await res.json()
    users.value = data.users
  }
}

async function loadKnowledge() {
  const res = await fetch('/api/admin/knowledge', { headers: authHeaders() })
  if (res.ok) {
    const data = await res.json()
    knowledgeFiles.value = data.files
    dataPath.value = data.data_path
  }
}

async function loadUserChats(userId) {
  const res = await fetch(`/api/admin/users/${userId}/chats`, { headers: authHeaders() })
  if (res.ok) {
    const data = await res.json()
    selectedUserChats.value = data.chats
  }
}

// ==================== 知识库操作 ====================

async function uploadFile(e) {
  const file = e.target.files[0]
  if (!file) return
  loading.value = true
  uploadMsg.value = ''
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await fetch('/api/admin/knowledge/upload', {
      method: 'POST',
      headers: authHeaders(),
      body: form,
    })
    const data = await res.json()
    if (data.duplicate) {
      uploadMsgOk.value = false
      uploadMsg.value = data.message
    } else if (data.ok) {
      uploadMsgOk.value = true
      uploadMsg.value = data.message
      await loadKnowledge()
    } else if (res.ok) {
      uploadMsgOk.value = true
      uploadMsg.value = data.message || `已上传: ${file.name}`
      await loadKnowledge()
    } else {
      uploadMsgOk.value = false
      uploadMsg.value = data.detail || data.message || '上传失败'
    }
  } catch {
    uploadMsgOk.value = false
    uploadMsg.value = '网络错误'
  }
  loading.value = false
  e.target.value = ''
}

async function viewFile(filename) {
  viewingFile.value = filename
  fileContent.value = '加载中...'
  fileContentType.value = ''
  try {
    const res = await fetch(`/api/admin/knowledge/${encodeURIComponent(filename)}/content`, {
      headers: authHeaders(),
    })
    const data = await res.json()
    fileContent.value = data.content || '(无内容)'
    fileContentType.value = data.type || ''
  } catch {
    fileContent.value = '加载失败'
  }
}

function closeViewer() {
  viewingFile.value = null
  fileContent.value = ''
}

async function deleteFile(filename) {
  if (!confirm(`确定删除 "${filename}" 吗？`)) return
  const res = await fetch(`/api/admin/knowledge/${encodeURIComponent(filename)}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  if (res.ok) {
    await loadKnowledge()
  }
}

async function reloadKnowledge() {
  if (!confirm('重新加载将清除缓存，让所有文档重新索引。确定继续？')) return
  const res = await fetch('/api/admin/knowledge/reload', {
    method: 'POST',
    headers: authHeaders(),
  })
  const data = await res.json()
  alert(data.message)
}

// ==================== 初始化 ====================

onMounted(async () => {
  await Promise.all([loadStats(), loadUsers(), loadKnowledge()])
})
</script>

<template>
  <div class="admin-page">
    <!-- 顶栏 -->
    <header class="admin-header">
      <h1>⚙️ 管理后台</h1>
      <div class="header-right">
        <span class="admin-name">{{ user?.username }}</span>
        <button class="btn-chat" @click="$router.push('/chat')">💬 返回聊天</button>
        <button class="btn-logout" @click="logout">退出登录</button>
      </div>
    </header>

    <!-- Tab 切换 -->
    <div class="admin-tabs">
      <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">👥 用户数据</button>
      <button :class="{ active: activeTab === 'knowledge' }" @click="activeTab = 'knowledge'">📚 知识库管理</button>
    </div>

    <!-- Tab: 用户数据 -->
    <div v-if="activeTab === 'users'" class="admin-content">
      <div class="stats-cards">
        <div class="stat-card"><strong>{{ stats.total_users }}</strong><span>总用户</span></div>
        <div class="stat-card"><strong>{{ stats.total_sessions }}</strong><span>总会话</span></div>
        <div class="stat-card"><strong>{{ stats.total_messages }}</strong><span>总消息</span></div>
      </div>

      <table class="user-table">
        <thead>
          <tr>
            <th>ID</th><th>用户名</th><th>角色</th><th>会话数</th><th>消息数</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td><span class="badge" :class="u.role">{{ u.role === 'admin' ? '管理员' : '用户' }}</span></td>
            <td>{{ u.session_count }}</td>
            <td>{{ u.message_count }}</td>
            <td>
              <button class="btn-sm" @click="loadUserChats(u.id)">查看聊天</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 用户聊天记录弹窗 -->
      <div v-if="selectedUserChats.length" class="chat-popup">
        <h3>最近聊天记录 <button class="btn-sm" @click="selectedUserChats = []">关闭</button></h3>
        <div v-for="c in selectedUserChats" :key="c.created_at" class="chat-item">
          <span class="chat-role" :class="c.role">{{ c.role === 'user' ? '👤' : '🤖' }}</span>
          <span class="chat-content">{{ c.content?.slice(0, 100) }}{{ c.content?.length > 100 ? '...' : '' }}</span>
          <span class="chat-time">{{ c.created_at?.slice(0, 16) }}</span>
        </div>
      </div>
    </div>

    <!-- Tab: 知识库管理 -->
    <div v-if="activeTab === 'knowledge'" class="admin-content">
      <div class="knowledge-actions">
        <label class="btn-upload">
          📤 上传文档
          <input type="file" accept=".pdf,.txt" hidden @change="uploadFile" />
        </label>
        <button class="btn-reload" @click="reloadKnowledge">🔄 重新加载向量库</button>
        <span class="knowledge-path">目录: {{ dataPath }}</span>
      </div>
      <p v-if="uploadMsg" class="upload-msg" :class="{ error: !uploadMsgOk }">{{ uploadMsg }}</p>

      <table class="user-table" v-if="knowledgeFiles.length">
        <thead>
          <tr><th>文件名</th><th>大小</th><th>MD5</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="f in knowledgeFiles" :key="f.name">
            <td>{{ f.name }}</td>
            <td>{{ f.size_str }}</td>
            <td class="md5-cell">{{ f.md5?.slice(0, 12) }}...</td>
            <td>
              <button class="btn-sm" @click="viewFile(f.name)">查看</button>
              <button class="btn-sm btn-danger" @click="deleteFile(f.name)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-hint">知识库暂无文件，请上传 PDF 或 TXT 文档</div>
    </div>

    <!-- 文件内容查看弹窗 -->
    <div v-if="viewingFile" class="modal-overlay" @click.self="closeViewer">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📄 {{ viewingFile }}</h3>
          <button class="btn-sm" @click="closeViewer">✕ 关闭</button>
        </div>
        <div class="modal-body">
          <p v-if="fileContentType === 'pdf'" class="pdf-hint">{{ fileContent }}</p>
          <pre v-else>{{ fileContent }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f3f4f6;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: #1e1b2e;
  color: #fff;
}

.admin-header h1 { margin: 0; font-size: 20px; }

.header-right { display: flex; align-items: center; gap: 12px; }

.admin-name {
  font-size: 14px;
  background: rgba(255,255,255,0.1);
  padding: 4px 10px;
  border-radius: 6px;
}

.btn-chat, .btn-logout {
  padding: 6px 14px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  background: transparent;
  color: #fff;
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
}

.btn-chat:hover, .btn-logout:hover { background: rgba(255,255,255,0.1); }

.admin-tabs {
  display: flex;
  padding: 0 32px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.admin-tabs button {
  padding: 14px 24px;
  border: none;
  background: none;
  font-size: 15px;
  color: #6b7280;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-family: inherit;
}

.admin-tabs button.active {
  color: #4f46e5;
  border-bottom-color: #4f46e5;
  font-weight: 600;
}

.admin-content { padding: 24px 32px; }

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.stat-card strong {
  display: block;
  font-size: 32px;
  color: #4f46e5;
}

.stat-card span {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 4px;
}

.user-table {
  width: 100%;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  border-collapse: collapse;
}

.user-table th {
  background: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-size: 13px;
  color: #6b7280;
}

.user-table td {
  padding: 12px 16px;
  border-top: 1px solid #f3f4f6;
  font-size: 14px;
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge.admin { background: #fef3c7; color: #92400e; }
.badge.user { background: #e0e7ff; color: #3730a3; }

.btn-sm {
  padding: 4px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
  font-family: inherit;
}

.btn-sm:hover { background: #f3f4f6; }
.btn-danger { color: #ef4444; border-color: #fecaca; }
.btn-danger:hover { background: #fef2f2; }

.chat-popup {
  margin-top: 24px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.chat-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
  font-size: 13px;
}

.chat-role { flex-shrink: 0; }
.chat-content { flex: 1; color: #374151; }
.chat-time { flex-shrink: 0; color: #9ca3af; font-size: 11px; }

.knowledge-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.btn-upload {
  padding: 10px 20px;
  background: #4f46e5;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
}

.btn-upload:hover { background: #4338ca; }

.btn-reload {
  padding: 10px 20px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
}

.knowledge-path {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}

.upload-msg { color: #10b981; font-size: 13px; margin-bottom: 12px; }
.upload-msg.error { color: #f59e0b; }

.md5-cell { font-size: 11px; color: #9ca3af; font-family: monospace; }

.empty-hint {
  text-align: center;
  padding: 40px;
  color: #9ca3af;
  font-size: 14px;
}

/* 文件内容查看弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 40px;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 { margin: 0; font-size: 16px; }

.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-body pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  margin: 0;
}

.pdf-hint {
  color: #9ca3af;
  font-style: italic;
  text-align: center;
  padding: 40px 0;
}
</style>
