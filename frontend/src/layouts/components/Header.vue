<template>
  <header class="header">
    <!-- 手機版漢堡選單 -->
    <button class="menu-btn" @click="$emit('toggle-sidebar')">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 12h18M3 6h18M3 18h18" />
      </svg>
    </button>

    <!-- 標題 -->
    <h1 class="header-title">{{ title }}</h1>

    <!-- 右側操作區 -->
    <div class="header-actions">
      <!-- 主題切換 -->
      <button class="icon-btn" @click="toggleTheme" :title="themeTitle">
        <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5" />
          <line x1="12" y1="1" x2="12" y2="3" />
          <line x1="12" y1="21" x2="12" y2="23" />
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
          <line x1="1" y1="12" x2="3" y2="12" />
          <line x1="21" y1="12" x2="23" y2="12" />
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
        </svg>
      </button>

      <!-- 用戶選單 -->
      <div class="user-menu">
        <button class="user-btn" @click="userMenuOpen = !userMenuOpen">
          <div class="avatar">
            {{ userInitial }}
          </div>
          <span class="username truncate">{{ user?.username || '用戶' }}</span>
          <svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>

        <div v-if="userMenuOpen" class="user-dropdown">
          <div class="user-info">
            <div class="user-email">{{ user?.email }}</div>
          </div>
          <div class="dropdown-divider" />
          <button class="dropdown-item" @click="logout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16,17 21,12 16,7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            登出
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const route = useRoute()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const theme = computed(() => themeStore.theme)
const user = computed(() => authStore.user)
const userInitial = computed(() => user.value?.username?.charAt(0).toUpperCase() || 'U')
const themeTitle = computed(() => theme.value === 'light' ? '切換到深色模式' : '切換到淺色模式')

const title = computed(() => {
  if (route.name === 'Documents') return '文件管理'
  return '對話'
})

const userMenuOpen = ref(false)

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  height: var(--header-height);
  padding: 0 var(--spacing-lg);
  background-color: var(--color-bg-elevated);
  border-bottom: 1px solid var(--color-border-light);
}

.menu-btn {
  display: none;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
}

.menu-btn:hover {
  background-color: var(--color-bg-tertiary);
}

.menu-btn svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 1023px) {
  .menu-btn {
    display: flex;
  }
}

.header-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-left: auto;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.icon-btn:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.icon-btn svg {
  width: 20px;
  height: 20px;
}

/* 用戶選單 */
.user-menu {
  position: relative;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--color-border-light);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
}

.user-btn:hover {
  border-color: var(--color-border);
}

.avatar {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-accent);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.username {
  max-width: 100px;
  font-size: var(--font-size-sm);
}

@media (max-width: 640px) {
  .username {
    display: none;
  }
}

.chevron {
  width: 14px;
  height: 14px;
  color: var(--color-text-tertiary);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  min-width: 180px;
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 100;
  overflow: hidden;
}

.user-info {
  padding: var(--spacing-md);
}

.user-email {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--color-border-light);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background: transparent;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  text-align: left;
  transition: background-color var(--transition-fast);
}

.dropdown-item:hover {
  background-color: var(--color-bg-tertiary);
}

.dropdown-item svg {
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
}
</style>
