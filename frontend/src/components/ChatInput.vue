<script setup>
import { ref } from 'vue'

defineProps({ disabled: Boolean })
const emit = defineEmits(['send'])

const input = ref('')

function handleSubmit() {
  const msg = input.value.trim()
  if (!msg) return
  emit('send', msg)
  input.value = ''
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div class="chat-input-container">
    <div class="chat-input-wrapper">
      <textarea
        v-model="input"
        class="chat-input"
        placeholder="输入您的问题，Enter 发送，Shift+Enter 换行"
        :disabled="disabled"
        rows="1"
        @keydown="handleKeydown"
        @input="(e) => {
          e.target.style.height = 'auto'
          e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px'
        }"
      />
      <button
        class="send-btn"
        :class="{ disabled: !input.trim() || disabled }"
        :disabled="!input.trim() || disabled"
        @click="handleSubmit"
      >
        <svg v-if="!disabled" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
      </button>
    </div>
    <p class="input-hint">智扫通可能产生不准确信息，请核实后使用</p>
  </div>
</template>

<style scoped>
.chat-input-container {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #ffffff;
  flex-shrink: 0;
}

.chat-input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 10px 14px;
  transition: border-color 0.2s;
}

.chat-input-wrapper:focus-within {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 15px;
  line-height: 1.5;
  resize: none;
  max-height: 150px;
  font-family: inherit;
  color: #1f2937;
}

.chat-input::placeholder {
  color: #c4b5cd;
}

.chat-input:disabled {
  opacity: 0.5;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: none;
  background: #4f46e5;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.send-btn:hover:not(.disabled) {
  background: #4338ca;
  transform: scale(1.05);
}

.send-btn.disabled {
  background: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

.input-hint {
  text-align: center;
  font-size: 11px;
  color: #d1d5db;
  margin: 8px 0 0;
}
</style>
