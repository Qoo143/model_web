<template>
  <div class="sidebar-container">
    <!-- Logo (可點擊返回首頁) -->
    <div class="sidebar-header">
      <router-link to="/" class="logo" title="返回首頁">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
        <span class="logo-text">Library RAG</span>
      </router-link>
      <button class="close-btn" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- 群組選擇器 -->
    <div class="group-selector">
      <button class="group-btn" @click="groupDropdownOpen = !groupDropdownOpen">
        <span class="group-name truncate">{{ chatStore.currentGroup?.name || '選擇群組' }}</span>
        <svg class="chevron" :class="{ 'chevron--open': groupDropdownOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>
      
      <div v-if="groupDropdownOpen" class="group-dropdown">
        <button 
          v-for="group in chatStore.groups" 
          :key="group.id"
          class="group-item"
          :class="{ 'group-item--active': chatStore.currentGroupId === group.id }"
          @click="handleSelectGroup(group.id)"
        >
          {{ group.name }}
        </button>
        <div v-if="chatStore.groups.length === 0" class="group-empty">
          尚無群組
        </div>
      </div>
    </div>

    <!-- 對話列表 -->
    <div class="conversations">
      <div class="section-header">
        <span>對話</span>
        <button class="new-chat-btn" @click="handleNewChat" title="新對話">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
      </div>
      
      <div class="conversation-list">
        <button 
          v-for="conv in chatStore.conversations" 
          :key="conv.id"
          class="conversation-item"
          :class="{ 'conversation-item--active': chatStore.currentConversationId === conv.id }"
          @click="handleSelectConversation(conv.id)"
        >
          <svg class="chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <span class="truncate">{{ conv.title }}</span>
        </button>
        
        <div v-if="chatStore.conversations.length === 0" class="empty-hint">
          點擊 + 開始新對話
        </div>
      </div>
    </div>

    <!-- 底部選單 -->
    <div class="sidebar-footer">
      <router-link to="/groups" class="footer-link" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
        <span>群組管理</span>
      </router-link>
      <router-link to="/documents" class="footer-link" @click="$emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14,2 14,8 20,8" />
        </svg>
        <span>文件管理</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'

defineEmits(['close'])

const router = useRouter()
const chatStore = useChatStore()
const groupDropdownOpen = ref(false)

const handleSelectGroup = (groupId: number) => {
  chatStore.selectGroup(groupId)
  groupDropdownOpen.value = false
}

const handleSelectConversation = (conversationId: number) => {
  chatStore.selectConversation(conversationId)
  router.push('/')
}

const handleNewChat = () => {
  chatStore.createNewConversation()
  router.push('/')
}

onMounted(() => {
  chatStore.fetchGroups()
})
</script>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: var(--spacing-md);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logo-icon {
  width: 24px;
  height: 24px;
  color: var(--color-accent);
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  transition: color var(--transition-fast);
}

.logo:hover .logo-text {
  color: var(--color-accent);
}

.close-btn {
  display: none;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
}

.close-btn:hover {
  background-color: var(--color-bg-tertiary);
}

@media (max-width: 1023px) {
  .close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

/* 群組選擇器 */
.group-selector {
  position: relative;
  margin-bottom: var(--spacing-lg);
}

.group-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.group-btn:hover {
  border-color: var(--color-accent);
}

.chevron {
  width: 16px;
  height: 16px;
  transition: transform var(--transition-fast);
}

.chevron--open {
  transform: rotate(180deg);
}

.group-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: var(--spacing-xs);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.group-item {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  text-align: left;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  transition: background-color var(--transition-fast);
}

.group-item:hover {
  background-color: var(--color-bg-tertiary);
}

.group-item--active {
  background-color: var(--color-accent-light);
  color: var(--color-accent);
}

.group-empty {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

/* 對話列表 */
.conversations {
  flex: 1;
  overflow-y: auto;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.new-chat-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.new-chat-btn:hover {
  background-color: var(--color-accent-light);
  color: var(--color-accent);
}

.new-chat-btn svg {
  width: 16px;
  height: 16px;
}

.conversation-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  text-align: left;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.conversation-item:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.conversation-item--active {
  background-color: var(--color-accent-light);
  color: var(--color-accent);
}

.chat-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.empty-hint {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

/* 底部 */
.sidebar-footer {
  margin-top: auto;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

.footer-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.footer-link:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.footer-link svg {
  width: 18px;
  height: 18px;
}
</style>
