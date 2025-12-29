---
name: frontend-state
description: >
  Pinia 狀態管理規範。當用戶詢問 "state"、"Pinia"、
  "store"、"狀態" 時觸發此 Skill。
tags: [frontend, pinia, state]
---

# 狀態管理規範

## Store 結構

```
frontend/src/stores/
├── auth.ts           # 認證狀態
├── chat.ts           # 對話狀態
└── document.ts       # 文件狀態
```

## Store 定義

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  // Actions
  async function login(credentials: LoginRequest) {
    const response = await authService.login(credentials)
    token.value = response.token
    user.value = response.user
  }
  
  function logout() {
    token.value = null
    user.value = null
  }
  
  return { user, token, isAuthenticated, isAdmin, login, logout }
})
```

## 使用方式

```vue
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()

// 解構響應式屬性
const { user, isAuthenticated } = storeToRefs(authStore)

// 呼叫 action
const handleLogin = async () => {
  await authStore.login({ username, password })
}
</script>
```

## 核心 Store

| Store | 說明 | 主要狀態 |
|:------|:-----|:---------|
| `auth` | 認證 | user, token |
| `chat` | 對話 | conversations, messages |
| `document` | 文件 | documents, uploadProgress |
