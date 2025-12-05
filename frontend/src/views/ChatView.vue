<template>
  <div class="chat-view">
    <!-- 訊息區域 -->
    <div class="messages-container" ref="messagesContainer">
      <!-- 空狀態 -->
      <div v-if="chatStore.messages.length === 0 && !chatStore.isLoading" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <h3>開始對話</h3>
        <p>輸入您的問題，我會根據文件內容為您解答</p>
        <div v-if="!chatStore.currentGroupId" class="hint">
          請先在側邊欄選擇一個群組
        </div>
      </div>

      <!-- 訊息列表 -->
      <div 
        v-for="message in chatStore.messages" 
        :key="message.id"
        class="message"
        :class="`message--${message.role}`"
      >
        <div class="message-avatar">
          <span v-if="message.role === 'user'">{{ userInitial }}</span>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v2m0 16v2M2 12h2m16 0h2" />
          </svg>
        </div>
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
          
          <!-- 來源引用 (可摺疊) -->
          <div v-if="message.sources?.length" class="sources">
            <button 
              class="sources-toggle" 
              @click="toggleSources(message.id)"
              type="button"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14,2 14,8 20,8" />
              </svg>
              <span>來源引用 ({{ message.sources.length }})</span>
              <svg 
                class="chevron" 
                :class="{ 'chevron--open': expandedSources.has(message.id) }"
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="2"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>
            <div v-if="expandedSources.has(message.id)" class="sources-list">
              <div 
                v-for="(source, idx) in message.sources" 
                :key="idx"
                class="source-card"
              >
                <div class="source-name">{{ source.document_name }}</div>
                <div class="source-content">{{ source.content }}</div>
                <div class="source-score">相關度: {{ (source.score * 100).toFixed(0) }}%</div>
              </div>
            </div>
          </div>

          <!-- 訊息時間 -->
          <div class="message-time">
            {{ formatTime(message.created_at) }}
          </div>
        </div>
      </div>

      <!-- 載入中 -->
      <div v-if="chatStore.isSending" class="message message--assistant">
        <div class="message-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v2m0 16v2M2 12h2m16 0h2" />
          </svg>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 輸入區域 -->
    <div class="input-area">
      <form @submit.prevent="handleSend" class="input-form">
        <input
          v-model="inputText"
          type="text"
          placeholder="輸入您的問題..."
          :disabled="chatStore.isSending || !chatStore.currentGroupId"
        />
        <button 
          type="submit" 
          :disabled="!inputText.trim() || chatStore.isSending || !chatStore.currentGroupId"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22,2 15,22 11,13 2,9" />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'

const authStore = useAuthStore()
const chatStore = useChatStore()

const userInitial = computed(() => authStore.user?.username?.charAt(0).toUpperCase() || 'U')

const messagesContainer = ref<HTMLElement | null>(null)
const inputText = ref('')

// 展開的來源引用集合 (預設摺疊)
const expandedSources = ref<Set<number>>(new Set())

const toggleSources = (messageId: number) => {
  if (expandedSources.value.has(messageId)) {
    expandedSources.value.delete(messageId)
  } else {
    expandedSources.value.add(messageId)
  }
  // 觸發響應式更新
  expandedSources.value = new Set(expandedSources.value)
}

const handleSend = async () => {
  if (!inputText.value.trim() || chatStore.isSending || !chatStore.currentGroupId) return

  const question = inputText.value.trim()
  inputText.value = ''
  
  await chatStore.sendMessage(question)
  scrollToBottom()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

// 監聽訊息變化，自動滾動
watch(() => chatStore.messages.length, () => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--header-height));
}

@media (max-width: 1023px) {
  .chat-view {
    height: calc(100vh - var(--header-height) - var(--mobile-nav-height));
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

/* 空狀態 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
  text-align: center;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--font-size-lg);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  color: var(--color-text-secondary);
}

.empty-state p {
  font-size: var(--font-size-sm);
}

.empty-state .hint {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-accent-light);
  border-radius: var(--radius-sm);
  color: var(--color-accent);
  font-size: var(--font-size-sm);
}

/* 訊息 */
.message {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.message--user .message-avatar {
  background-color: var(--color-accent);
  color: white;
}

.message--assistant .message-avatar {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
}

.message--assistant .message-avatar svg {
  width: 20px;
  height: 20px;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  line-height: 1.7;
  color: var(--color-text-primary);
  white-space: pre-wrap;
}

.message--assistant .message-text {
  padding: var(--spacing-md);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-xs);
}

/* 來源引用 (可摺疊) */
.sources {
  margin-top: var(--spacing-md);
}

.sources-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  width: 100%;
}

.sources-toggle:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.sources-toggle svg:first-child {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.sources-toggle span {
  flex: 1;
  text-align: left;
}

.sources-toggle .chevron {
  width: 16px;
  height: 16px;
  transition: transform var(--transition-fast);
}

.sources-toggle .chevron--open {
  transform: rotate(180deg);
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.source-card {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-bg-tertiary);
  border-left: 3px solid var(--color-accent);
  border-radius: var(--radius-sm);
}

.source-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-accent);
  margin-bottom: var(--spacing-xs);
}

.source-content {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.source-score {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-xs);
}

/* 載入動畫 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: var(--spacing-md);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  width: fit-content;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: var(--color-text-tertiary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 輸入區域 */
.input-area {
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--color-bg-elevated);
  border-top: 1px solid var(--color-border-light);
}

.input-form {
  display: flex;
  gap: var(--spacing-sm);
  max-width: 800px;
  margin: 0 auto;
}

.input-form input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
}

.input-form input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.input-form input::placeholder {
  color: var(--color-text-tertiary);
}

.input-form input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-form button {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background-color: var(--color-accent);
  color: white;
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
}

.input-form button:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.input-form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-form button svg {
  width: 20px;
  height: 20px;
}
</style>
