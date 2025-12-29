---
name: backend-api
description: >
  FastAPI API 開發規範。當用戶詢問 "API"、"endpoint"、
  "route"、"controller"、"請求處理" 時觸發此 Skill。
tags: [backend, api, fastapi]
---

# API 開發規範

## 路由結構

```
backend/app/api/
├── __init__.py
├── deps.py          # 依賴注入
├── auth.py          # 認證 API
├── documents.py     # 文件管理 API
└── chat.py          # 對話 API
```

## 路由命名規範

| 操作 | HTTP Method | 路徑模式 | 範例 |
|:-----|:------------|:---------|:-----|
| 列表 | GET | `/resources` | `GET /documents` |
| 單筆 | GET | `/resources/{id}` | `GET /documents/1` |
| 建立 | POST | `/resources` | `POST /documents` |
| 更新 | PUT | `/resources/{id}` | `PUT /documents/1` |
| 刪除 | DELETE | `/resources/{id}` | `DELETE /documents/1` |

## 依賴注入模式

```python
from fastapi import Depends
from app.api.deps import get_current_user, get_db

@router.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ...
```

## 錯誤處理

```python
from fastapi import HTTPException, status

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Document not found"
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Permission denied"
)
```

## 詳細參考

→ [reference/api-patterns.md](./reference/api-patterns.md) - 完整 API 設計模式
