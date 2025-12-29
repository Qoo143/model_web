---
name: frontend-skills
description: >
  前端開發技能集合。包含 Components、State Management 等主題。
  當用戶詢問 Vue、組件、Pinia 相關問題時觸發。
tags: [frontend, vue, typescript]
---

# Frontend Skills

前端使用 **Vue 3** + **TypeScript** + **Tailwind CSS** + **Pinia** 架構。

## 子主題

| Skill | 說明 | 觸發關鍵字 |
|:------|:-----|:-----------|
| [components](./components/SKILL.md) | 組件開發 | component, Vue, 組件 |
| [state](./state/SKILL.md) | 狀態管理 | state, Pinia, store |

## 目錄結構

```
frontend/src/
├── components/        # Vue 組件
│   ├── chat/         # 對話相關
│   ├── document/     # 文件管理
│   ├── auth/         # 認證相關
│   └── common/       # 通用組件
├── views/             # 頁面視圖
├── stores/            # Pinia 狀態
├── services/          # API 服務
├── types/             # TypeScript 型別
├── router/            # Vue Router
└── utils/             # 工具函數
```

## 技術規範

- **Vue 3**: 使用 Composition API (`<script setup>`)
- **TypeScript**: 嚴格模式
- **Tailwind CSS**: Utility-first 樣式
- **Vite**: 建置工具
