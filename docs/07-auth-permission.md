# 07. 認證與權限系統 - JWT 與群組權限

## 為什麼需要認證系統？

想像一個沒有門鎖的圖書館：

```
沒有認證系統:
任何人都可以:
  - 看所有文件（包括機密文件）
  - 刪除別人的文件
  - 修改系統設定

問題:
❌ 沒有隱私
❌ 沒有安全性
❌ 無法追蹤誰做了什麼

有認證系統:
1. 登入時出示身份證（帳號密碼）
2. 取得通行證（JWT Token）
3. 進入時檢查通行證
4. 只能訪問有權限的區域

優點:
✅ 隱私保護
✅ 權限控制
✅ 操作可追蹤
```

---

## 認證系統架構

```
┌─────────────────────────────────────────────────┐
│ 1. 使用者註冊                                     │
│    username + password → 儲存到資料庫              │
│    (密碼加密,不儲存明文)                           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 2. 使用者登入                                     │
│    輸入 username + password                      │
│    驗證成功 → 發放 JWT Token                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 3. 訪問受保護的 API                               │
│    請求 Header 帶上 JWT Token                    │
│    Authorization: Bearer eyJhbGc...              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 4. 後端驗證 Token                                │
│    解析 Token → 取得 user_id                     │
│    檢查 Token 是否過期                            │
│    檢查使用者權限                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 5. 執行操作 / 返回錯誤                            │
│    權限足夠 → 執行操作                            │
│    權限不足 → 返回 403 Forbidden                  │
└─────────────────────────────────────────────────┘
```

---

## JWT (JSON Web Token) 詳解

### 什麼是 JWT？

**比喻**: JWT 就像遊樂園的手環

```
傳統方式（Session）:
1. 入園時給你一個號碼牌（Session ID）
2. 每次玩遊戲都要去櫃檯查你的資料
3. 伺服器要記住所有人的資料（佔記憶體）

JWT 方式:
1. 入園時給你一個手環（包含你的資訊）
2. 手環上寫著: 「姓名: Alice, VIP等級: Gold, 有效期: 今天」
3. 每個遊戲只要看手環就知道你的權限
4. 伺服器不用記住你（無狀態）

JWT 優點:
✅ 無狀態（伺服器不用儲存 session）
✅ 跨域友善（適合前後端分離）
✅ 可攜帶使用者資訊
✅ 可設定過期時間
```

### JWT 結構

JWT 由三部分組成，用 `.` 分隔：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFsaWNlIiwiZXhwIjoxNjE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
       ↑                                  ↑                                                            ↑
     Header                            Payload                                                   Signature
   (演算法資訊)                        (實際資料)                                                  (簽章驗證)
```

**Header (標頭)**:
```json
{
  "alg": "HS256",  // 加密演算法
  "typ": "JWT"     // 類型
}
```

**Payload (負載)**:
```json
{
  "user_id": 1,
  "username": "alice",
  "role": "user",
  "exp": 1616239022  // 過期時間（Unix timestamp）
}
```

**Signature (簽章)**:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key  // 密鑰（只有伺服器知道）
)
```

**重要**:
- Header 和 Payload 是 Base64 編碼（不是加密！）
- 任何人都可以解碼看到內容
- 但只有知道 secret_key 的人才能驗證和生成

---

## 密碼加密 (bcrypt)

### 為什麼不能儲存明文密碼？

```
❌ 危險做法:
database:
  users:
    - username: alice
      password: "password123"  ← 明文！

問題:
- 資料庫被駭 → 所有密碼外洩
- 內部人員可以看到密碼
- 使用者在其他網站用相同密碼會被盜用

✅ 安全做法:
database:
  users:
    - username: alice
      password: "$2b$12$LQv3c1yqBWVH..."  ← 加密後的 hash

優點:
- 即使資料庫被駭，也無法反推原始密碼
- 內部人員也看不到密碼
- 每個密碼的 hash 都不同（加鹽）
```

### bcrypt 運作原理

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 註冊時: 將密碼加密
plain_password = "password123"
hashed = pwd_context.hash(plain_password)
print(hashed)
# 輸出: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NAuJC6eJWJfC

# 登入時: 驗證密碼
is_correct = pwd_context.verify("password123", hashed)
print(is_correct)  # True

is_correct = pwd_context.verify("wrong_password", hashed)
print(is_correct)  # False
```

**重要特性**:
- **單向加密**: 無法從 hash 反推原始密碼
- **加鹽 (Salt)**: 相同密碼每次加密結果都不同
- **慢速演算法**: 故意設計得慢（防止暴力破解）

---

## 實作認證系統

### 步驟 1: 設定密碼加密

```python
# backend/app/core/security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 設定
SECRET_KEY = "your-secret-key-please-change-in-production"  # 從環境變數讀取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    加密密碼

    Args:
        password: 明文密碼

    Returns:
        加密後的 hash
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼

    Args:
        plain_password: 明文密碼
        hashed_password: 資料庫中的 hash

    Returns:
        是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)
```

### 步驟 2: JWT Token 生成與驗證

```python
# backend/app/core/security.py (續)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT Token

    Args:
        data: 要編碼的資料 (通常包含 user_id, username)
        expires_delta: 過期時間（可選）

    Returns:
        JWT Token 字串
    """
    to_encode = data.copy()

    # 設定過期時間
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # 編碼成 JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解碼並驗證 JWT Token

    Args:
        token: JWT Token 字串

    Returns:
        解碼後的資料，如果無效則返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None  # Token 無效或過期
```

### 步驟 3: 註冊 API

```python
# backend/app/api/auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.security import hash_password
from app.models.user import User
from app.core.database import get_db

router = APIRouter(prefix="/api/auth", tags=["認證"])

class UserRegister(BaseModel):
    """註冊請求"""
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """使用者回應"""
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    註冊新使用者

    業務邏輯:
    1. 檢查 username 和 email 是否已存在
    2. 加密密碼
    3. 建立使用者記錄
    4. 返回使用者資訊（不包含密碼）
    """
    # 檢查 username 是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者名稱已被使用"
        )

    # 檢查 email 是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="電子郵件已被註冊"
        )

    # 建立新使用者
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),  # 加密密碼
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
```

### 步驟 4: 登入 API

```python
# backend/app/api/auth.py (續)

from datetime import timedelta
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

class UserLogin(BaseModel):
    """登入請求"""
    username: str
    password: str

class Token(BaseModel):
    """Token 回應"""
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    使用者登入

    業務邏輯:
    1. 驗證使用者名稱和密碼
    2. 生成 JWT Token
    3. 返回 Token 和使用者資訊
    """
    # 查詢使用者
    user = db.query(User).filter(User.username == login_data.username).first()

    # 驗證使用者存在且密碼正確
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 檢查帳號是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已被停用"
        )

    # 生成 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
```

### 步驟 5: 取得當前使用者（Dependency）

```python
# backend/app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.models.user import User
from app.core.database import get_db

# HTTP Bearer Token 認證
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    取得當前登入的使用者

    依賴注入（Dependency Injection）:
    - 從 Authorization Header 中提取 Token
    - 驗證 Token 並解碼
    - 從資料庫取得使用者

    使用方式:
    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"message": f"Hello {current_user.username}"}
    """
    # 提取 Token
    token = credentials.credentials

    # 解碼 Token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的認證憑證",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 取得 user_id
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 格式錯誤"
        )

    # 從資料庫查詢使用者
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已被停用"
        )

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """簡化版本：取得當前啟用的使用者"""
    return current_user
```

---

## 群組權限系統

### 權限層級

```python
# backend/app/models/group.py

from enum import Enum

class GroupRole(str, Enum):
    """群組角色（權限由高到低）"""
    OWNER = "owner"      # 擁有者
    ADMIN = "admin"      # 管理員
    EDITOR = "editor"    # 編輯者
    VIEWER = "viewer"    # 檢視者

# 權限層級對照
ROLE_HIERARCHY = {
    GroupRole.OWNER: 3,
    GroupRole.ADMIN: 2,
    GroupRole.EDITOR: 1,
    GroupRole.VIEWER: 0
}

def role_level(role: GroupRole) -> int:
    """取得角色的權限等級"""
    return ROLE_HIERARCHY.get(role, -1)

def has_permission(user_role: GroupRole, required_role: GroupRole) -> bool:
    """
    檢查使用者角色是否滿足所需權限

    Args:
        user_role: 使用者的角色
        required_role: 所需的最低角色

    Returns:
        是否有權限

    範例:
        has_permission(OWNER, VIEWER) → True (owner >= viewer)
        has_permission(VIEWER, ADMIN) → False (viewer < admin)
    """
    return role_level(user_role) >= role_level(required_role)
```

### 權限檢查函數

```python
# backend/app/utils/permissions.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember, GroupRole
from app.models.user import User

def check_group_permission(
    db: Session,
    user_id: int,
    group_id: int,
    required_role: GroupRole = GroupRole.VIEWER
) -> GroupMember:
    """
    檢查使用者在群組中的權限

    Args:
        db: 資料庫 session
        user_id: 使用者 ID
        group_id: 群組 ID
        required_role: 所需的最低角色

    Returns:
        GroupMember 物件（如果有權限）

    Raises:
        HTTPException: 如果沒有權限
    """
    # 查詢使用者在該群組的成員身份
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.is_active == True
    ).first()

    # 不是群組成員
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是此群組的成員"
        )

    # 檢查角色權限
    if not has_permission(GroupRole(member.role), required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"此操作需要 {required_role.value} 或更高權限"
        )

    return member

def get_accessible_documents(
    db: Session,
    user_id: int,
    group_id: int
) -> list:
    """
    取得使用者在群組中可訪問的文件 ID 列表

    權限邏輯:
    - owner: 可看所有文件
    - admin: 可看 admin/editor/viewer 級別的文件
    - editor: 可看 editor/viewer 級別的文件
    - viewer: 只能看 viewer 級別的文件
    """
    # 取得使用者的群組角色
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()

    if not member:
        return []  # 不是成員，無法訪問任何文件

    # 根據角色決定可訪問的文件級別
    user_level = role_level(GroupRole(member.role))

    accessible_roles = [
        role.value for role, level in ROLE_HIERARCHY.items()
        if level <= user_level
    ]

    # 查詢可訪問的文件
    from app.models.document import Document

    documents = db.query(Document).filter(
        Document.group_id == group_id,
        Document.processing_status == "completed",
        Document.min_view_role.in_(accessible_roles)
    ).all()

    return [doc.id for doc in documents]
```

### API 權限保護

```python
# backend/app/api/documents.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import Document
from app.api.deps import get_current_user
from app.core.database import get_db
from app.utils.permissions import check_group_permission, GroupRole

router = APIRouter(prefix="/api/documents", tags=["文件"])

@router.get("/group/{group_id}")
def list_group_documents(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    列出群組的所有文件

    權限要求: viewer 或以上
    """
    # 檢查權限（至少要是 viewer）
    check_group_permission(
        db=db,
        user_id=current_user.id,
        group_id=group_id,
        required_role=GroupRole.VIEWER
    )

    # 取得可訪問的文件
    accessible_doc_ids = get_accessible_documents(db, current_user.id, group_id)

    documents = db.query(Document).filter(
        Document.id.in_(accessible_doc_ids)
    ).all()

    return documents

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    刪除文件

    權限要求: editor 或以上
    """
    # 查詢文件
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 檢查權限（需要 editor 或以上）
    check_group_permission(
        db=db,
        user_id=current_user.id,
        group_id=document.group_id,
        required_role=GroupRole.EDITOR
    )

    # 額外檢查：只有上傳者或管理員可以刪除
    member = check_group_permission(db, current_user.id, document.group_id, GroupRole.VIEWER)

    if document.uploaded_by != current_user.id and member.role not in [GroupRole.ADMIN.value, GroupRole.OWNER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文件上傳者或群組管理員可以刪除文件"
        )

    # 刪除文件
    db.delete(document)
    db.commit()

    return {"message": "文件已刪除"}
```

---

## 前端整合

### 儲存 Token

```typescript
// frontend/src/services/auth.service.ts

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email: string;
    role: string;
  };
}

class AuthService {
  /**
   * 登入
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('登入失敗');
    }

    const data: LoginResponse = await response.json();

    // 儲存 Token 到 localStorage
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));

    return data;
  }

  /**
   * 登出
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  /**
   * 取得 Token
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * 檢查是否已登入
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * 取得當前使用者
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}

export default new AuthService();
```

### API 請求攔截器

```typescript
// frontend/src/services/api.ts

import axios from 'axios';
import authService from './auth.service';

// 建立 Axios 實例
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// 請求攔截器：自動加上 Token
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器：處理 401 錯誤
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 過期或無效，導向登入頁
      authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 路由守衛（Vue Router）

```typescript
// frontend/src/router/index.ts

import { createRouter, createWebHistory } from 'vue-router';
import authService from '@/services/auth.service';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/chat',
      name: 'Chat',
      component: () => import('@/views/ChatView.vue'),
      meta: { requiresAuth: true },  // 需要登入
    },
    {
      path: '/documents',
      name: 'Documents',
      component: () => import('@/views/DocumentsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
});

// 路由守衛
router.beforeEach((to, from, next) => {
  const requiresAuth = to.meta.requiresAuth;
  const isAuthenticated = authService.isAuthenticated();

  if (requiresAuth && !isAuthenticated) {
    // 需要登入但未登入，導向登入頁
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.name === 'Login' && isAuthenticated) {
    // 已登入但訪問登入頁，導向首頁
    next({ name: 'Chat' });
  } else {
    next();
  }
});

export default router;
```

---

## 安全最佳實踐

### 1. 密碼強度要求

```python
import re

def validate_password(password: str) -> tuple[bool, str]:
    """
    驗證密碼強度

    要求:
    - 至少 8 個字元
    - 包含大寫字母
    - 包含小寫字母
    - 包含數字
    - 包含特殊字元
    """
    if len(password) < 8:
        return False, "密碼至少需要 8 個字元"

    if not re.search(r"[A-Z]", password):
        return False, "密碼需包含至少一個大寫字母"

    if not re.search(r"[a-z]", password):
        return False, "密碼需包含至少一個小寫字母"

    if not re.search(r"[0-9]", password):
        return False, "密碼需包含至少一個數字"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "密碼需包含至少一個特殊字元"

    return True, "密碼強度足夠"

# 在註冊時使用
@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 驗證密碼強度
    is_valid, message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # ... 繼續註冊流程
```

### 2. Rate Limiting（速率限制）

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 每分鐘最多 5 次登入嘗試
def login(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    # ... 登入邏輯
    pass
```

### 3. CORS 設定

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 前端開發環境
        "https://yourdomain.com"  # 生產環境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. HTTPS Only（生產環境）

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# 生產環境強制使用 HTTPS
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 常見問題

### Q1: Token 過期了怎麼辦？

**A**: 實作 Refresh Token 機制

```python
# 生成兩種 Token
access_token = create_access_token(data, expires_delta=timedelta(minutes=30))  # 短效
refresh_token = create_access_token(data, expires_delta=timedelta(days=7))    # 長效

# 前端：access_token 過期時用 refresh_token 換新的
@router.post("/refresh")
def refresh_token(refresh_token: str):
    payload = decode_access_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token 無效")

    new_access_token = create_access_token(data={"user_id": payload["user_id"]})
    return {"access_token": new_access_token}
```

### Q2: 如何防止暴力破解？

**A**:
1. Rate Limiting（限制登入嘗試次數）
2. 帳號鎖定（連續失敗 5 次鎖定 15 分鐘）
3. CAPTCHA 驗證碼
4. 記錄可疑登入並通知使用者

### Q3: Token 儲存在哪裡？

**A**:
- ✅ **推薦**: localStorage（方便但有 XSS 風險）
- ⚠️ **可選**: Cookie（HttpOnly, Secure）
- ❌ **不推薦**: sessionStorage（關閉分頁就消失）

---

## 下一步

現在你已經掌握認證與權限系統，最後一步：

1. **完整後端實作**: [08. 後端實作指南](08-backend-implementation.md)

---

## 延伸閱讀

- [JWT 官方網站](https://jwt.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP 認證備忘單](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
