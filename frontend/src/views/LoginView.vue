<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo -->
      <div class="login-header">
        <svg class="logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
        </svg>
        <h1>Library RAG Agent</h1>
        <p>智能文件問答系統</p>
      </div>

      <!-- 表單切換 -->
      <div class="form-tabs">
        <button 
          class="tab" 
          :class="{ 'tab--active': mode === 'login' }"
          @click="mode = 'login'"
        >
          登入
        </button>
        <button 
          class="tab" 
          :class="{ 'tab--active': mode === 'register' }"
          @click="mode = 'register'"
        >
          註冊
        </button>
      </div>

      <!-- 登入表單 -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="form">
        <div class="form-group">
          <label for="username">使用者名稱</label>
          <input 
            id="username"
            v-model="loginForm.username"
            type="text"
            placeholder="請輸入使用者名稱"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密碼</label>
          <input 
            id="password"
            v-model="loginForm.password"
            type="password"
            placeholder="請輸入密碼"
            required
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner" />
          {{ isLoading ? '登入中...' : '登入' }}
        </button>
      </form>

      <!-- 註冊表單 -->
      <form v-else @submit.prevent="handleRegister" class="form">
        <div class="form-group">
          <label for="reg-username">使用者名稱</label>
          <input 
            id="reg-username"
            v-model="registerForm.username"
            type="text"
            placeholder="請輸入使用者名稱"
            required
          />
        </div>

        <div class="form-group">
          <label for="reg-email">電子郵件</label>
          <input 
            id="reg-email"
            v-model="registerForm.email"
            type="email"
            placeholder="請輸入電子郵件"
            required
          />
        </div>

        <div class="form-group">
          <label for="reg-password">密碼</label>
          <input 
            id="reg-password"
            v-model="registerForm.password"
            type="password"
            placeholder="請輸入密碼 (至少6位)"
            minlength="6"
            required
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner" />
          {{ isLoading ? '註冊中...' : '註冊' }}
        </button>
      </form>
    </div>

    <!-- 主題切換 -->
    <button class="theme-toggle" @click="toggleTheme">
      <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5" />
        <line x1="12" y1="1" x2="12" y2="3" />
        <line x1="12" y1="21" x2="12" y2="23" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const mode = ref<'login' | 'register'>('login')
const error = ref('')
const successMessage = ref('')
const isLoading = computed(() => authStore.isLoading)
const theme = computed(() => themeStore.theme)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  error.value = ''
  const result = await authStore.login(loginForm.username, loginForm.password)
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.message || '登入失敗'
  }
}

const handleRegister = async () => {
  error.value = ''
  successMessage.value = ''
  
  const result = await authStore.register(
    registerForm.username,
    registerForm.email,
    registerForm.password
  )
  
  if (result.success) {
    successMessage.value = '註冊成功！請登入'
    mode.value = 'login'
    loginForm.username = registerForm.username
    registerForm.username = ''
    registerForm.email = ''
    registerForm.password = ''
  } else {
    error.value = result.message || '註冊失敗'
  }
}

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background-color: var(--color-bg-primary);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo {
  width: 48px;
  height: 48px;
  color: var(--color-accent);
  margin-bottom: var(--spacing-md);
}

.login-header h1 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.login-header p {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.form-tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.tab {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  background-color: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.tab:hover {
  background-color: var(--color-bg-tertiary);
}

.tab--active {
  background-color: var(--color-accent);
  color: white;
}

.form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-group label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-group input {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.form-group input::placeholder {
  color: var(--color-text-tertiary);
}

.error-message {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: rgba(199, 90, 90, 0.1);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-sm);
  color: var(--color-error);
  font-size: var(--font-size-sm);
}

.success-message {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: rgba(92, 154, 107, 0.1);
  border: 1px solid var(--color-success);
  border-radius: var(--radius-sm);
  color: var(--color-success);
  font-size: var(--font-size-sm);
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  background-color: var(--color-accent);
  color: white;
  font-size: var(--font-size-base);
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
  margin-top: var(--spacing-sm);
}

.submit-btn:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.theme-toggle {
  position: fixed;
  bottom: var(--spacing-lg);
  right: var(--spacing-lg);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border);
  background-color: var(--color-bg-elevated);
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.theme-toggle svg {
  width: 20px;
  height: 20px;
}
</style>
