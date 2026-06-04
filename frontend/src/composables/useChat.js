import { ref, nextTick } from 'vue'

export function useChat(authHeadersFn) {
  const messages = ref([])
  const isLoading = ref(false)
  const thinkingText = ref('')
  const messagesContainer = ref(null)
  const currentSessionId = ref(null)
  const sessions = ref([])
  const loadingSessions = ref(false)

  function addMessage(role, content) {
    messages.value.push({ role, content, id: Date.now() + Math.random() })
  }

  function updateLastMessage(content) {
    if (messages.value.length > 0) {
      messages.value[messages.value.length - 1].content = content
    }
  }

  function appendToLastMessage(chunk) {
    if (messages.value.length > 0) {
      messages.value[messages.value.length - 1].content += chunk
    }
  }

  async function scrollToBottom() {
    await nextTick()
    const el = messagesContainer.value
    if (el) el.scrollTop = el.scrollHeight
  }

  function summarizeThinking(content) {
    if (!content) return '正在思考...'
    const firstLine = content.split('\n')[0].trim()
    if (firstLine.length <= 30) return firstLine
    return firstLine.slice(0, 30) + '...'
  }

  // ==================== 会话管理 ====================

  async function fetchSessions() {
    loadingSessions.value = true
    try {
      const res = await fetch('/api/sessions', { headers: authHeadersFn() })
      if (res.ok) {
        const data = await res.json()
        sessions.value = data.sessions
      }
    } catch {
      // ignore
    } finally {
      loadingSessions.value = false
    }
  }

  async function createNewSession() {
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { ...authHeadersFn(), 'Content-Type': 'application/json' },
      })
      if (res.ok) {
        const data = await res.json()
        sessions.value.unshift({ id: data.id, title: '新对话', created_at: new Date().toISOString() })
        currentSessionId.value = data.id
        messages.value = []
      }
    } catch {
      // ignore
    }
  }

  async function switchSession(sessionId) {
    if (currentSessionId.value === sessionId) return
    currentSessionId.value = sessionId
    messages.value = []
    thinkingText.value = ''

    try {
      const res = await fetch(`/api/sessions/${sessionId}/messages`, {
        headers: authHeadersFn(),
      })
      if (res.ok) {
        const data = await res.json()
        for (const msg of data.messages) {
          addMessage(msg.role, msg.content)
        }
      }
    } catch {
      // ignore
    }
    await scrollToBottom()
  }

  async function deleteCurrentSession() {
    const sid = currentSessionId.value
    if (!sid) return
    try {
      await fetch(`/api/sessions/${sid}`, {
        method: 'DELETE',
        headers: authHeadersFn(),
      })
      sessions.value = sessions.value.filter(s => s.id !== sid)
      messages.value = []
      currentSessionId.value = null
      // 切换到剩余的第一个会话，或创建新会话
      if (sessions.value.length > 0) {
        await switchSession(sessions.value[0].id)
      } else {
        await createNewSession()
      }
    } catch {
      // ignore
    }
  }

  // ==================== 发送消息 ====================

  async function sendMessage(message) {
    if (!message.trim() || isLoading.value) return

    addMessage('user', message)
    addMessage('assistant', '')
    isLoading.value = true
    thinkingText.value = ''
    await scrollToBottom()

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { ...authHeadersFn(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: currentSessionId.value }),
      })

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed || !trimmed.startsWith('data: ')) continue
          const data = trimmed.slice(6)
          if (data === '[DONE]') continue

          try {
            const parsed = JSON.parse(data)

            switch (parsed.type) {
              case 'thinking':
                thinkingText.value = summarizeThinking(parsed.content)
                await scrollToBottom()
                break
              case 'answer':
                thinkingText.value = ''
                appendToLastMessage(parsed.content)
                await scrollToBottom()
                break
              case 'error':
                thinkingText.value = ''
                updateLastMessage(`系统错误：${parsed.content}`)
                break
              case 'meta':
                // session_id 元信息，忽略
                break
              default:
                appendToLastMessage(parsed.content)
                await scrollToBottom()
            }
          } catch {
            // ignore
          }
        }
      }
      thinkingText.value = ''
    } catch (err) {
      thinkingText.value = ''
      updateLastMessage(`网络错误：${err.message}`)
    } finally {
      isLoading.value = false
      // 刷新会话列表（标题可能已更新）
      await fetchSessions()
    }
  }

  function clearMessages() {
    messages.value = []
    thinkingText.value = ''
  }

  async function loadSessionMessages(sessionId) {
    await switchSession(sessionId)
  }

  return {
    messages, isLoading, thinkingText, messagesContainer,
    currentSessionId, sessions, loadingSessions,
    sendMessage, clearMessages, loadSessionMessages,
    fetchSessions, createNewSession, switchSession, deleteCurrentSession,
    scrollToBottom,
  }
}
