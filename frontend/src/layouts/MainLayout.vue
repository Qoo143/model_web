<template>
  <div class="main-layout">
    <!-- 側邊欄 -->
    <aside 
      class="sidebar" 
      :class="{ 'sidebar--collapsed': isMobile && !sidebarOpen }"
    >
      <Sidebar @close="sidebarOpen = false" />
    </aside>

    <!-- 遮罩 (手機版) -->
    <div 
      v-if="isMobile && sidebarOpen" 
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    />

    <!-- 主內容區 -->
    <main class="main-content">
      <Header @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <div class="page-content">
        <router-view />
      </div>
    </main>

    <!-- 手機底部導航 -->
    <MobileNav v-if="isMobile" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import MobileNav from './components/MobileNav.vue'

const sidebarOpen = ref(false)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 1024
  if (!isMobile.value) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg-primary);
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background-color: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-light);
  z-index: 100;
  transition: transform var(--transition-base);
}

@media (max-width: 1023px) {
  .sidebar {
    transform: translateX(0);
  }
  
  .sidebar--collapsed {
    transform: translateX(-100%);
  }
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 99;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: var(--sidebar-width);
  min-width: 0;
}

@media (max-width: 1023px) {
  .main-content {
    margin-left: 0;
  }
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: var(--mobile-nav-height);
}

@media (min-width: 1024px) {
  .page-content {
    padding-bottom: 0;
  }
}
</style>
