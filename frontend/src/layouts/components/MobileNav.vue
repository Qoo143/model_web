<template>
  <nav class="mobile-nav">
    <router-link 
      to="/" 
      class="nav-item"
      :class="{ 'nav-item--active': route.name === 'Chat' }"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <span>對話</span>
    </router-link>

    <router-link 
      to="/documents" 
      class="nav-item"
      :class="{ 'nav-item--active': route.name === 'Documents' }"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14,2 14,8 20,8" />
      </svg>
      <span>文件</span>
    </router-link>

    <router-link 
      to="/groups" 
      class="nav-item"
      :class="{ 'nav-item--active': route.name === 'Groups' }"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
      <span>群組</span>
    </router-link>

    <button class="nav-item" @click="toggleTheme">
      <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5" />
        <line x1="12" y1="1" x2="12" y2="3" />
        <line x1="12" y1="21" x2="12" y2="23" />
      </svg>
      <span>主題</span>
    </button>

    <button class="nav-item" @click="logout">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
        <polyline points="16,17 21,12 16,7" />
        <line x1="21" y1="12" x2="9" y2="12" />
      </svg>
      <span>登出</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

const theme = computed(() => themeStore.theme)

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.mobile-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--mobile-nav-height);
  display: flex;
  align-items: center;
  justify-content: space-around;
  background-color: var(--color-bg-elevated);
  border-top: 1px solid var(--color-border-light);
  z-index: 100;
}

@media (min-width: 1024px) {
  .mobile-nav {
    display: none;
  }
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--spacing-sm);
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: 11px;
  text-decoration: none;
  transition: color var(--transition-fast);
}

.nav-item:hover,
.nav-item--active {
  color: var(--color-accent);
}

.nav-item svg {
  width: 22px;
  height: 22px;
}
</style>
