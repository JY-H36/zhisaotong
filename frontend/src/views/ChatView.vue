<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
import ChatArea from '../components/ChatArea.vue'
import { useChat } from '../composables/useChat.js'
import { useAuth } from '../composables/useAuth.js'

const router = useRouter()
const { user, authHeaders, logout } = useAuth()
const showSidebar = ref(true)

const {
  messages, isLoading, thinkingText, messagesContainer,
  sendMessage, clearMessages, loadSessionMessages,
  currentSessionId, sessions, loadingSessions,
  fetchSessions, createNewSession, switchSession, deleteCurrentSession,
} = useChat(authHeaders)

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

function goAdmin() {
  router.push('/admin')
}

onMounted(async () => {
  await fetchSessions()
  // 如果有会话，切换到最近一个；否则创建新会话
  if (sessions.value.length > 0) {
    await switchSession(sessions.value[0].id)
  } else {
    await createNewSession()
  }
})
</script>

<template>
  <div class="app-layout">
    <Sidebar
      :show="showSidebar"
      :sessions="sessions"
      :current-session-id="currentSessionId"
      :loading-sessions="loadingSessions"
      @toggle="toggleSidebar"
      @new-session="createNewSession"
      @switch-session="switchSession"
      @delete-session="deleteCurrentSession"
    />
    <ChatArea
      :messages="messages"
      :is-loading="isLoading"
      :thinking-text="thinkingText"
      :show-sidebar="showSidebar"
      :messages-container="messagesContainer"
      :user="user"
      @toggle-sidebar="toggleSidebar"
      @send="sendMessage"
      @logout="logout"
      @go-admin="goAdmin"
    />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}
</style>
