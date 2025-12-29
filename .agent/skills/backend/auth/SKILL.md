---
name: backend-auth
description: >
  認證授權系統規範。當用戶詢問 "auth"、"JWT"、"login"、
  "permission"、"token"、"權限" 時觸發此 Skill。
tags: [backend, auth, jwt, security]
---

# 認證授權規範

## JWT Token 結構

```python
{
    "user_id": 1,
    "username": "alice",
    "role": "user",        # user | admin
    "exp": 1234567890      # 過期時間
}
```

## 權限等級

| 角色 | 說明 | 權限 |
|:-----|:-----|:-----|
| `owner` | 群組擁有者 | 完整權限 |
| `admin` | 管理員 | 管理成員、文件 |
| `editor` | 編輯者 | 上傳、刪除文件 |
| `viewer` | 檢視者 | 只能查看和問答 |

## 依賴注入

```python
from app.api.deps import get_current_user, require_permission

# 取得當前用戶
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

# 權限檢查
@router.delete("/documents/{id}")
@require_permission("editor")
async def delete_document(
    id: int,
    current_user: User = Depends(get_current_user)
):
    ...
```

## 密碼加密

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密
hashed = pwd_context.hash(password)

# 驗證
pwd_context.verify(plain_password, hashed_password)
```

## 詳細參考

→ [reference/auth-flow.md](./reference/auth-flow.md) - 完整認證流程
