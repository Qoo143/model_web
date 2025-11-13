# 前端測試說明

## 目錄結構

```
frontend/tests/
├── unit/       # 單元測試 - 測試單一組件或函數
└── e2e/        # 端對端測試 - 測試完整使用者流程
```

## 單元測試 (unit/)

使用 Vitest 測試單一組件或工具函數。

**範例**:
- 測試 Vue 組件渲染
- 測試 Pinia store 邏輯
- 測試工具函數 (format, validate)
- 測試 API service 函數

**測試框架**: Vitest + Vue Test Utils

## 端對端測試 (e2e/)

使用 Playwright 或 Cypress 測試完整的使用者操作流程。

**範例**:
- 測試完整的登入流程
- 測試文件上傳到查詢的完整流程
- 測試多輪對話功能
- 測試群組管理功能

**測試框架**: Playwright (推薦) 或 Cypress

## 執行測試

```bash
# 執行所有單元測試
npm run test:unit

# 執行單元測試 (watch mode)
npm run test:unit:watch

# 執行端對端測試
npm run test:e2e

# 執行端對端測試 (headless mode)
npm run test:e2e:headless
```

## 測試命名規範

- 測試文件: `*.spec.ts` 或 `*.test.ts`
- 組件測試: `ComponentName.spec.ts`
- 工具測試: `utils.spec.ts`

**範例**:
```typescript
// tests/unit/components/ChatInterface.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatInterface from '@/components/chat/ChatInterface.vue'

describe('ChatInterface', () => {
  it('renders properly', () => {
    const wrapper = mount(ChatInterface)
    expect(wrapper.exists()).toBe(true)
  })

  it('sends message on submit', async () => {
    const wrapper = mount(ChatInterface)
    // 測試邏輯...
  })
})
```

## E2E 測試範例

```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('http://localhost:5173/login')

  await page.fill('input[name="username"]', 'testuser')
  await page.fill('input[name="password"]', 'test123')
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL('http://localhost:5173/chat')
})
```
