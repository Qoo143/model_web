---
name: frontend-components
description: >
  Vue 組件開發規範。當用戶詢問 "component"、"組件"、
  "Vue"、"props"、"emit" 時觸發此 Skill。
tags: [frontend, vue, components]
---

# 組件開發規範

## 命名規範

| 類型 | 命名 | 範例 |
|:-----|:-----|:-----|
| 頁面組件 | PascalCase + View | `ChatView.vue` |
| UI 組件 | PascalCase | `MessageBubble.vue` |
| 通用組件 | PascalCase | `Button.vue` |

## 組件結構

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

// Props
interface Props {
  message: string
  isUser?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  isUser: false
})

// Emits
const emit = defineEmits<{
  (e: 'click', id: number): void
}>()

// State
const isLoading = ref(false)

// Computed
const displayMessage = computed(() => props.message.trim())
</script>

<template>
  <div :class="['message', { 'user': isUser }]">
    {{ displayMessage }}
  </div>
</template>

<style scoped>
.message {
  @apply p-4 rounded-lg;
}
.message.user {
  @apply bg-blue-500 text-white;
}
</style>
```

## 核心組件

| 組件 | 說明 | 路徑 |
|:-----|:-----|:-----|
| `ChatInterface` | 主對話介面 | `components/chat/` |
| `MessageBubble` | 訊息氣泡 | `components/chat/` |
| `DocumentUpload` | 上傳元件 | `components/document/` |
| `DocumentList` | 文件列表 | `components/document/` |
