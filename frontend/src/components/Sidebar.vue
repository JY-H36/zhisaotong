<script setup>
defineProps({
  show: Boolean,
  sessions: Array,
  currentSessionId: Number,
  loadingSessions: Boolean,
})

const emit = defineEmits(['toggle', 'new-session', 'switch-session', 'delete-session'])

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString()
}
</script>

<template>
  <Transition name="slide">
    <aside v-if="show" class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <span class="logo-icon">🤖</span>
          <span class="logo-text">智扫通</span>
        </div>
        <button class="btn-icon" title="收起侧边栏" @click="emit('toggle')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      </div>

      <div class="sidebar-actions">
        <button class="btn-new-chat" @click="emit('new-session')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>新对话</span>
        </button>
      </div>

      <!-- 会话列表 -->
      <div class="session-list">
        <div v-if="loadingSessions" class="session-loading">加载中...</div>
        <div
          v-for="sess in sessions"
          :key="sess.id"
          class="session-item"
          :class="{ active: sess.id === currentSessionId }"
          @click="emit('switch-session', sess.id)"
        >
          <div class="session-title">{{ sess.title }}</div>
          <div class="session-time">{{ formatTime(sess.updated_at) }}</div>
          <button
            class="btn-delete"
            title="删除会话"
            @click.stop="emit('switch-session', sess.id); emit('delete-session')"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
            </svg>
          </button>
        </div>
        <div v-if="!loadingSessions && sessions.length === 0" class="session-empty">
          暂无对话
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="sidebar-hint">智能客服 · 随时为您服务</div>
      </div>
    </aside>
  </Transition>
</template>

<style scoped>
.sidebar {
  width: 280px;
  min-width: 280px;
  height: 100vh;
  background: #1e1b2e;
  display: flex;
  flex-direction: column;
  color: #e0dce8;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon { font-size: 26px; }

.logo-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.btn-icon {
  background: none;
  border: none;
  color: #9b95b0;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #e0dce8;
}

.sidebar-actions {
  padding: 16px;
  flex-shrink: 0;
}

.btn-new-chat {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #e0dce8;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-new-chat:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 会话列表 */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
}

.session-loading,
.session-empty {
  text-align: center;
  color: #6b6580;
  font-size: 13px;
  padding: 24px 0;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  gap: 8px;
  margin-bottom: 2px;
}

.session-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.session-item.active {
  background: rgba(79, 70, 229, 0.2);
}

.session-title {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #d1d5db;
}

.session-item.active .session-title {
  color: #e0dce8;
  font-weight: 500;
}

.session-time {
  font-size: 11px;
  color: #6b6580;
  flex-shrink: 0;
}

.btn-delete {
  background: none;
  border: none;
  color: #6b6580;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all 0.15s;
  display: flex;
}

.session-item:hover .btn-delete {
  opacity: 1;
}

.btn-delete:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.15);
}

.sidebar-footer {
  margin-top: auto;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.sidebar-hint {
  font-size: 12px;
  color: #6b6580;
  text-align: center;
}

/* 侧边栏滑入滑出 */
.slide-enter-active,
.slide-leave-active { transition: all 0.3s ease; }
.slide-enter-from,
.slide-leave-to {
  width: 0; min-width: 0; opacity: 0; padding: 0; overflow: hidden;
}
</style>
