# 08. 後端實作指南 - FastAPI 完整實作

## 專案結構回顧

```
backend/
├── app/
│   ├── main.py              # FastAPI 應用入口
│   ├── __init__.py
│   │
│   ├── models/              # SQLAlchemy 資料庫模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── document.py
│   │   └── conversation.py
│   │
│   ├── schemas/             # Pydantic 資料驗證
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── document.py
│   │   └── chat.py
│   │
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── deps.py          # 依賴注入
│   │   ├── auth.py          # 認證 API
│   │   ├── groups.py        # 群組 API
│   │   ├── documents.py     # 文件 API
│   │   └── chat.py          # 對話 API
│   │
│   ├── services/            # 業務邏輯
│   │   ├── __init__.py
│   │   ├── llm/             # LLM 服務
│   │   │   ├── base.py
│   │   │   ├── ollama_service.py
│   │   │   └── factory.py
│   │   ├── rag/             # RAG 核心
│   │   │   ├── embedder.py
│   │   │   ├── vectorstore.py
│   │   │   └── retriever.py
│   │   └── document/        # 文件處理
│   │       ├── parser.py
│   │       ├── chunker.py
│   │       └── processor.py
│   │
│   ├── core/                # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py        # 設定管理
│   │   ├── security.py      # 安全相關
│   │   └── database.py      # 資料庫連線
│   │
│   └── utils/               # 工具函數
│       ├── __init__.py
│       └── permissions.py
│
├── tests/                   # 測試
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── requirements.txt         # Python 依賴
└── alembic.ini             # 資料庫遷移配置
```

---

## 步驟 1: 建立基礎配置

### 1.1 核心配置

```python
# backend/app/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    應用程式配置

    從環境變數讀取配置
    優先級: 環境變數 > .env 檔案 > 預設值
    """

    # 應用程式
    APP_NAME: str = "Library RAG Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 資料庫
    DATABASE_URL: str = "mysql+aiomysql://library_user:library_pass@mysql:3306/library_agent"

    # JWT
    SECRET_KEY: str = "your-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "gpt-oss-20b"

    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DEVICE: str = "cpu"

    # Chroma
    CHROMA_PERSIST_DIRECTORY: str = "./storage/chroma_db"

    # 文件上傳
    UPLOAD_DIR: str = "./storage/documents"
    MAX_FILE_SIZE: int = 52428800  # 50MB

    # RAG 配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

# 單例模式
settings = Settings()
```

### 1.2 資料庫連線

```python
# backend/app/core/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 建立非同步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 開發時顯示 SQL
    pool_pre_ping=True,   # 檢查連線是否有效
    pool_size=10,         # 連線池大小
    max_overflow=20       # 最大溢出連線數
)

# Session 工廠
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base 類別（所有 Model 繼承）
Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    資料庫 Session 依賴注入

    使用方式:
    @router.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## 步驟 2: 建立資料庫模型

### 2.1 User Model

```python
# backend/app/models/user.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    """系統角色"""
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """使用者模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

### 2.2 Group 和 GroupMember Models

```python
# backend/app/models/group.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class GroupRole(str, enum.Enum):
    """群組角色"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Group(Base):
    """群組模型"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    is_private = Column(Boolean, default=True)
    allow_join_request = Column(Boolean, default=False)

    member_count = Column(Integer, default=1)
    document_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="group", cascade="all, delete-orphan")

class GroupMember(Base):
    """群組成員模型"""
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(GroupRole), default=GroupRole.VIEWER, nullable=False)

    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    invited_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True)

    # 關聯
    group = relationship("Group", back_populates="members")
```

### 2.3 Document Model

```python
# backend/app/models/document.py

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DocumentStatus(str, enum.Enum):
    """文件處理狀態"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    """文件模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)  # UUID 檔名
    original_filename = Column(String(255), nullable=False)  # 原始檔名
    file_type = Column(String(20), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(500), nullable=False)

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    min_view_role = Column(Enum("owner", "admin", "editor", "viewer"), default="viewer")

    processing_status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    error_message = Column(Text)

    chunk_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    group = relationship("Group", back_populates="documents")
```

---

## 步驟 3: Pydantic Schemas

### 3.1 User Schemas

```python
# backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """使用者基礎 Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """註冊時使用"""
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """登入時使用"""
    username: str
    password: str

class UserResponse(UserBase):
    """返回給前端的使用者資訊（不包含密碼）"""
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2

class Token(BaseModel):
    """JWT Token 回應"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

### 3.2 Document Schemas

```python
# backend/app/schemas/document.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentUpload(BaseModel):
    """文件上傳請求"""
    group_id: int
    min_view_role: str = "viewer"

class DocumentResponse(BaseModel):
    """文件回應"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    group_id: int
    uploaded_by: int
    processing_status: str
    chunk_count: int
    page_count: int
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## 步驟 4: API 路由實作

### 4.1 認證 API

```python
# backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from datetime import timedelta
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["認證"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    註冊新使用者

    業務流程:
    1. 檢查 username 和 email 是否已存在
    2. 驗證密碼強度
    3. 加密密碼
    4. 建立使用者記錄
    5. 返回使用者資訊
    """
    # 檢查 username
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者名稱已被使用"
        )

    # 檢查 email
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="電子郵件已被註冊"
        )

    # 建立使用者
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    使用者登入

    業務流程:
    1. 驗證帳號密碼
    2. 生成 JWT Token
    3. 返回 Token 和使用者資訊
    """
    # 查詢使用者
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()

    # 驗證密碼
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼錯誤"
        )

    # 檢查帳號狀態
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已被停用"
        )

    # 生成 Token
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
```

### 4.2 文件上傳 API

```python
# backend/app/api/documents.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.utils.permissions import check_group_permission, GroupRole
from app.services.document.processor import DocumentProcessor
import uuid
from pathlib import Path
from app.core.config import settings

router = APIRouter(prefix="/api/documents", tags=["文件"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    group_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上傳文件

    業務流程:
    1. 檢查權限（需要 editor 或以上）
    2. 驗證檔案（格式、大小）
    3. 儲存檔案
    4. 建立資料庫記錄
    5. 啟動背景任務處理文件
    """
    # 檢查權限
    await check_group_permission(db, current_user.id, group_id, GroupRole.EDITOR)

    # 檢查檔案類型
    allowed_types = {"pdf", "docx", "xlsx", "txt", "md"}
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支援的檔案格式。支援: {', '.join(allowed_types)}"
        )

    # 檢查檔案大小
    file.file.seek(0, 2)  # 移到檔案末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 回到開頭

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"檔案過大。最大: {settings.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )

    # 生成唯一檔名
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    user_dir = Path(settings.UPLOAD_DIR) / f"user_{current_user.id}"
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / unique_filename

    # 儲存檔案
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 建立資料庫記錄
    document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_type=file_ext,
        file_size=file_size,
        file_path=str(file_path),
        group_id=group_id,
        uploaded_by=current_user.id,
        processing_status="pending"
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # TODO: 啟動背景任務
    # process_document_task.delay(document.id)

    return document
```

### 4.3 RAG 問答 API

```python
# backend/app/api/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.rag.retriever import RAGService
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/chat", tags=["對話"])

class ChatRequest(BaseModel):
    """問答請求"""
    question: str
    group_id: int
    document_ids: Optional[List[int]] = None
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    """問答回應"""
    answer: str
    sources: List[dict]
    conversation_id: int
    message_id: int

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    RAG 問答

    業務流程:
    1. 檢查權限（需要是群組成員）
    2. 檢索相關文件
    3. 呼叫 LLM 生成答案
    4. 儲存對話記錄
    5. 返回答案和來源
    """
    # 檢查權限
    await check_group_permission(db, current_user.id, request.group_id, GroupRole.VIEWER)

    # 初始化 RAG 服務
    rag_service = RAGService()

    # 問答
    result = await rag_service.query(
        question=request.question,
        group_id=request.group_id,
        document_ids=request.document_ids,
        user_id=current_user.id
    )

    # TODO: 儲存對話記錄

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "conversation_id": 1,  # TODO
        "message_id": 1  # TODO
    }
```

---

## 步驟 5: FastAPI 主程式

```python
# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, documents, chat, groups
from app.core.config import settings

# 建立 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
# app.include_router(groups.router)

@app.get("/")
def root():
    """根路徑"""
    return {
        "message": f"歡迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
```

---

## 步驟 6: Requirements.txt

```txt
# backend/requirements.txt

# FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
aiomysql==0.2.0
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Pydantic
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# LLM & RAG
langchain==0.1.0
langchain-community==0.0.10
ollama==0.1.6

# Embedding & Vector Store
sentence-transformers==2.2.2
chromadb==0.4.18

# Document Processing
PyMuPDF==1.23.8  # PDF
python-docx==1.1.0  # Word
openpyxl==3.1.2  # Excel

# Utilities
python-dotenv==1.0.0
```

---

## 步驟 7: 啟動應用

### 7.1 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

### 7.2 設定環境變數

```bash
cp ../.env.example .env
# 編輯 .env 修改設定
```

### 7.3 資料庫遷移（Alembic）

```bash
# 初始化 Alembic
alembic init alembic

# 建立遷移檔
alembic revision --autogenerate -m "Initial tables"

# 執行遷移
alembic upgrade head
```

### 7.4 啟動應用

```bash
# 開發模式（自動重載）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Docker
cd ..
docker-compose up -d backend
```

### 7.5 測試 API

瀏覽器開啟:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 測試流程

### 1. 註冊使用者

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

### 2. 登入

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }'

# 複製返回的 access_token
```

### 3. 上傳文件

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@test.pdf" \
  -F "group_id=1"
```

### 4. 問答

```bash
curl -X POST "http://localhost:8000/api/chat/ask" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "這份文件的主要內容是什麼？",
    "group_id": 1
  }'
```

---

## 常見問題

### Q1: 如何除錯？

**A**:
```python
# 1. 開啟 DEBUG 模式
# .env
DEBUG=True

# 2. 查看日誌
docker-compose logs -f backend

# 3. 使用 breakpoint()
def my_function():
    breakpoint()  # 程式會在這裡暫停
    ...
```

### Q2: 如何新增 API 端點？

**A**:
1. 在對應的路由檔案新增函數
2. 定義 Pydantic Schema
3. 實作業務邏輯
4. 測試（/docs）

### Q3: 如何處理非同步？

**A**:
```python
# FastAPI 支援 async/await
@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

---

## 下一步開發

### 後續功能

1. **群組管理 API**
   - 建立群組
   - 邀請成員
   - 修改權限

2. **對話管理**
   - 儲存對話記錄
   - 對話列表
   - 對話標題生成

3. **文件管理增強**
   - 文件預覽
   - 文件搜尋
   - 批次上傳

4. **背景任務**
   - Celery 整合
   - 文件處理佇列
   - 進度追蹤

5. **監控與日誌**
   - 結構化日誌
   - 效能監控
   - 錯誤追蹤

---

## 延伸閱讀

- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文件](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 文件](https://docs.pydantic.dev/)
- [Alembic 遷移指南](https://alembic.sqlalchemy.org/)

---

**恭喜！你已經完成所有教學文件的學習！**

現在你可以：
1. 回顧 [專案概述](01-project-overview.md) 理解全貌
2. 動手實作每個模組
3. 根據需求客製化功能

祝你開發順利！🚀
