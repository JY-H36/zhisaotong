<script setup>
import { computed } from 'vue'

const props = defineProps({
  role: String,       // 'user' | 'assistant'
  content: String,
  isStreaming: Boolean,
})

const avatar = computed(() => (props.role === 'user' ? '👤' : '🤖'))
const label = computed(() => (props.role === 'user' ? '您' : '智扫通'))
</script>

<template>
  <div v-if="content" class="message" :class="[role, { streaming: isStreaming }]">
    <div class="message-avatar">{{ avatar }}</div>
    <div class="message-body">
      <div class="message-label">{{ label }}</div>
      <div class="message-content">{{ content }}<span v-if="isStreaming" class="cursor-blink">▍</span></div>
    </div>
  </div>
</template>

<style scoped>
.message {
  display: flex;
  gap: 14px;
  max-width: 85%;
  animation: fadeIn 0.3s ease;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.message-avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.user .message-avatar {
  background: #eef2ff;
}

.assistant .message-avatar {
  background: #f5f3ff;
}

.message-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
  font-weight: 500;
}

.message-content {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.user .message-content {
  background: #4f46e5;
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.assistant .message-content {
  background: #f9fafb;
  color: #1f2937;
  border: 1px solid #f3f4f6;
  border-bottom-left-radius: 4px;
}

/* 流式光标闪烁 */
.cursor-blink {
  animation: blink 1s step-end infinite;
  color: #4f46e5;
}

@keyframes blink {
  50% { opacity: 0; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
