<script setup>
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'

const props = defineProps({
  messages: Array,
  isLoading: Boolean,
  thinkingText: String,
  showSidebar: Boolean,
  messagesContainer: Object,
  user: Object,
})

const emit = defineEmits(['toggle-sidebar', 'send', 'logout', 'go-admin'])
</script>

<template>
  <div class="chat-area">
    <!-- 顶栏 -->
    <header class="chat-header">
      <button
        v-if="!showSidebar"
        class="btn-icon"
        title="展开侧边栏"
        @click="emit('toggle-sidebar')"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
      <h1 class="chat-title">智扫通机器人智能客服</h1>
      <span class="chat-user" v-if="user">{{ user.username }}</span>
      <button
        v-if="user && user.role === 'admin'"
        class="btn-admin"
        title="管理后台"
        @click="emit('go-admin')"
      >
        ⚙️
      </button>
      <button class="btn-logout" title="退出登录" @click="emit('logout')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </svg>
      </button>
    </header>

    <!-- 消息列表 -->
    <div ref="messagesContainer" class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">🏠</div>
        <h2>欢迎使用智扫通</h2>
        <p>您可以向我询问关于扫地机器人的任何问题</p>
        <div class="suggestion-grid">
          <button
            v-for="q in ['今天上海的天气怎么样？', '小户型适合哪些扫地机器人？', '帮我查看我的使用报告']"
            :key="q"
            class="suggestion-chip"
            @click="emit('send', q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <ChatMessage
        v-for="msg in messages"
        :key="msg.id"
        :role="msg.role"
        :content="msg.content"
        :is-streaming="isLoading && msg.role === 'assistant' && msg === messages[messages.length - 1]"
      />

      <!-- 思考状态指示器：Agent 在调用工具 / 检索资料 -->
      <div v-if="isLoading && thinkingText" class="thinking-bar">
        <div class="thinking-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <span class="thinking-label">{{ thinkingText }}</span>
      </div>
    </div>

    <!-- 输入区 -->
    <ChatInput :disabled="isLoading" @send="emit('send', $event)" />
  </div>
</template>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #ffffff;
  min-width: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  flex-shrink: 0;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  flex: 1;
}

.chat-user {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 10px;
  border-radius: 6px;
}

.btn-logout {
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: #fef2f2;
  color: #ef4444;
}

.btn-admin {
  background: none;
  border: none;
  color: #f59e0b;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 18px;
  transition: all 0.2s;
}

.btn-admin:hover {
  background: #fef3c7;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.empty-state h2 {
  font-size: 22px;
  color: #1f2937;
  margin: 0 0 8px;
  font-weight: 600;
}

.empty-state p {
  color: #9ca3af;
  font-size: 14px;
  margin: 0 0 24px;
}

.suggestion-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 360px;
  width: 100%;
}

.suggestion-chip {
  padding: 12px 18px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  color: #374151;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.suggestion-chip:hover {
  background: #f3f4f6;
  border-color: #4f46e5;
  color: #4f46e5;
}

/* 思考状态条 */
.thinking-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  background: #fefce8;
  border: 1px solid #fde68a;
  border-radius: 12px;
  align-self: flex-start;
  animation: fadeIn 0.3s ease;
}

.thinking-dots {
  display: flex;
  gap: 4px;
}

.thinking-label {
  font-size: 13px;
  color: #92400e;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
