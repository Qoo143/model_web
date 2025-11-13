# 圖書館 RAG Agent 系統 - 專案架構文件

## 專案概述

這是一個基於 RAG（Retrieval-Augmented Generation）技術的企業級智能文件問答系統。
使用者可以上傳各種格式的文件（PDF、Word、Excel、Markdown），系統會自動解析、向量化並建立知識索引。
透過自然語言對話，使用者可以精確查詢文件內容，系統會引用來源並提供詳細答案。

### 核心價值

- **知識集中管理**: 將分散的文件整合到統一平台
- **智能檢索**: 不需要記住確切的關鍵字，用自然語言提問即可
- **來源可追溯**: 每個答案都附帶引用來源，確保資訊可靠性
- **權限管控**: 不同使用者只能訪問其權限範圍內的文件

## 技術棧選擇說明

### 前端技術

- **Vue 3 + TypeScript**:
  - Vue 3 提供響應式資料綁定和組合式 API
  - TypeScript 增強程式碼可靠性和開發體驗
  - 組件化開發，易於維護和擴展

- **Tailwind CSS**:
  - Utility-first 設計，快速建立一致的 UI
  - 減少 CSS 檔案大小
  - 高度可定製

- **Vite**:
  - 極快的熱更新（HMR）
  - 基於 ES Module 的開發伺服器
  - 優化的生產構建

- **Pinia**:
  - Vue 3 官方狀態管理
  - TypeScript 支援良好
  - 模組化設計

### 後端技術

- **FastAPI**:
  - 高效能非同步框架（基於 Starlette 和 Pydantic）
  - 自動生成 OpenAPI 文檔
  - 原生支援 WebSocket（用於即時對話）
  - 完善的型別提示支援

- **SQLAlchemy 2.0**:
  - 強大的 Python ORM
  - 支援非同步操作
  - 跨資料庫相容

- **LangChain**:
  - LLM 應用開發框架
  - 內建 RAG 組件
  - 豐富的文件處理工具
  - 向量資料庫整合

### AI/ML 組件

- **Ollama**:
  - 本地運行 LLM 的最佳解決方案
  - 支援 AMD GPU（透過 ROCm）
  - Docker 友善
  - 與 OpenAI API 相容的介面
  - 簡單的模型管理

- **gpt-oss-20b**:
  - 20B 參數的開源語言模型
  - 中英文支援良好
  - 可在 16GB VRAM 上運行（量化版）

- **BGE-M3**:
  - BAAI 開發的多語言 Embedding 模型
  - 中文效果優秀
  - 支援長文本（最長 8192 tokens）
  - 統一的語意空間

- **Chroma**:
  - 輕量級向量資料庫
  - Python 原生，易於整合
  - 支援過濾和元資料查詢
  - 持久化儲存

### 資料庫與儲存

- **MySQL 8.0**:
  - 成熟穩定的關聯式資料庫
  - 儲存使用者資訊、文件元資料、對話記錄
  - JSON 欄位支援（儲存來源引用等）
  - 完善的權限控制

- **本地檔案系統**:
  - 原始文件儲存在 `storage/documents/`
  - Chroma 資料庫儲存在 `storage/chroma_db/`
  - 簡單、可靠、易於備份
  - 未來可遷移到 S3/MinIO

### 基礎設施

- **Docker + Docker Compose**:
  - 確保開發和生產環境一致
  - 簡化部署流程
  - 隔離各個服務
  - 支援 GPU（nvidia-docker 或 ROCm）

## 專案結構

```
library_agent/
├── frontend/                    # 前端 Vue 應用
│   ├── src/
│   │   ├── components/         # Vue 組件
│   │   │   ├── chat/          # 對話相關
│   │   │   │   ├── ChatInterface.vue      # 主對話介面
│   │   │   │   ├── MessageBubble.vue      # 訊息氣泡
│   │   │   │   ├── SourceReference.vue    # 來源引用卡片
│   │   │   │   └── DocumentSelector.vue   # 文件選擇器
│   │   │   ├── document/      # 文件管理
│   │   │   │   ├── DocumentUpload.vue     # 上傳元件
│   │   │   │   ├── DocumentList.vue       # 文件列表
│   │   │   │   └── DocumentCard.vue       # 文件卡片
│   │   │   ├── auth/          # 認證相關
│   │   │   │   ├── LoginForm.vue          # 登入表單
│   │   │   │   └── RegisterForm.vue       # 註冊表單
│   │   │   └── common/        # 通用組件
│   │   │       ├── Button.vue
│   │   │       ├── Input.vue
│   │   │       └── Modal.vue
│   │   │
│   │   ├── views/             # 頁面視圖
│   │   │   ├── ChatView.vue              # 對話頁面
│   │   │   ├── DocumentsView.vue         # 文件管理頁面
│   │   │   ├── LoginView.vue             # 登入頁面
│   │   │   └── ProfileView.vue           # 個人資料頁面
│   │   │
│   │   ├── stores/            # Pinia 狀態管理
│   │   │   ├── auth.ts                   # 認證狀態
│   │   │   ├── chat.ts                   # 對話狀態
│   │   │   └── document.ts               # 文件狀態
│   │   │
│   │   ├── services/          # API 服務
│   │   │   ├── api.ts                    # Axios 配置
│   │   │   ├── auth.service.ts           # 認證 API
│   │   │   ├── chat.service.ts           # 對話 API
│   │   │   └── document.service.ts       # 文件 API
│   │   │
│   │   ├── types/             # TypeScript 型別
│   │   │   ├── auth.ts
│   │   │   ├── chat.ts
│   │   │   └── document.ts
│   │   │
│   │   ├── router/            # Vue Router
│   │   │   └── index.ts
│   │   │
│   │   ├── utils/             # 工具函數
│   │   │   ├── format.ts
│   │   │   └── validate.ts
│   │   │
│   │   ├── App.vue            # 根組件
│   │   └── main.ts            # 應用入口
│   │
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                    # 後端 FastAPI 應用
│   ├── app/
│   │   ├── models/            # SQLAlchemy 資料庫模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py                   # 使用者模型
│   │   │   ├── document.py               # 文件模型
│   │   │   ├── conversation.py           # 對話模型
│   │   │   └── message.py                # 訊息模型
│   │   │
│   │   ├── schemas/           # Pydantic 資料驗證模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py                   # 使用者 schema
│   │   │   ├── document.py               # 文件 schema
│   │   │   └── chat.py                   # 對話 schema
│   │   │
│   │   ├── services/          # 業務邏輯層
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── llm/           # LLM 服務（低耦合設計）
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py               # 抽象基類
│   │   │   │   ├── ollama_service.py     # Ollama 實作
│   │   │   │   ├── gemini_service.py     # Gemini 實作（未來）
│   │   │   │   └── factory.py            # 工廠模式選擇
│   │   │   │
│   │   │   ├── rag/           # RAG 核心邏輯
│   │   │   │   ├── __init__.py
│   │   │   │   ├── embedder.py           # Embedding 服務
│   │   │   │   ├── vectorstore.py        # Chroma 向量庫操作
│   │   │   │   ├── retriever.py          # 檢索策略
│   │   │   │   └── chain.py              # RAG Chain
│   │   │   │
│   │   │   ├── document/      # 文件處理
│   │   │   │   ├── __init__.py
│   │   │   │   ├── parser.py             # 文件解析（PDF/Word/Excel）
│   │   │   │   ├── chunker.py            # 語意分塊
│   │   │   │   └── processor.py          # 處理流程協調
│   │   │   │
│   │   │   ├── auth/          # 認證服務
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jwt.py                # JWT 處理
│   │   │   │   └── password.py           # 密碼加密
│   │   │   │
│   │   │   └── user_service.py           # 使用者業務邏輯
│   │   │
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                   # 依賴注入
│   │   │   ├── auth.py                   # 認證 API
│   │   │   ├── documents.py              # 文件管理 API
│   │   │   └── chat.py                   # 對話 API
│   │   │
│   │   ├── core/              # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py                 # 配置類別
│   │   │   ├── security.py               # 安全相關
│   │   │   └── database.py               # 資料庫連線
│   │   │
│   │   ├── utils/             # 工具函數
│   │   │   ├── __init__.py
│   │   │   ├── file_handler.py           # 檔案操作
│   │   │   └── permissions.py            # 權限檢查
│   │   │
│   │   └── main.py            # FastAPI 應用入口
│   │
│   ├── requirements.txt        # Python 依賴
│   ├── alembic/               # 資料庫遷移
│   │   └── versions/
│   └── alembic.ini
│
├── storage/                    # 本地儲存（不提交到 Git）
│   ├── documents/             # 原始文件
│   │   └── {user_id}/        # 按使用者分類
│   └── chroma_db/            # Chroma 向量資料庫
│
├── docker/                     # Docker 配置
│   ├── backend/
│   │   └── Dockerfile
│   ├── frontend/
│   │   └── Dockerfile
│   ├── mysql/
│   │   └── init.sql          # 資料庫初始化
│   └── ollama/
│       └── Dockerfile        # Ollama GPU 配置
│
├── docs/                       # 詳細文檔
│   ├── 01-architecture.md                # 架構說明
│   ├── 02-docker-setup.md                # Docker 設置
│   ├── 03-rag-implementation.md          # RAG 實作
│   ├── 04-document-processing.md         # 文件處理
│   ├── 05-ollama-integration.md          # Ollama 整合
│   └── 06-auth-system.md                 # 認證系統
│
├── docker-compose.yml          # 服務編排
├── .env.example               # 環境變數範例
├── .gitignore
└── README.md                  # 專案說明
```

## 核心功能模組

### 1. 使用者認證與授權

**功能**:
- 使用者註冊/登入
- JWT Token 認證
- 基於角色的權限控制（user/admin）
- 會話管理

**技術實作**:
```python
# JWT Token 包含：
{
  "user_id": 1,
  "username": "alice",
  "role": "user",
  "exp": 1234567890  # 過期時間
}

# 權限裝飾器
@require_permission("read_document")
def get_document(doc_id: int, user: User):
    ...
```

### 2. 文件管理系統

**功能**:
- 文件上傳（支援多種格式）
- 文件列表展示
- 文件刪除
- 文件搜尋
- 處理狀態追蹤

**文件處理流程**:
```
上傳 → 驗證 → 解析 → 分塊 → 向量化 → 儲存 → 完成
        ↓      ↓     ↓      ↓       ↓
      格式   提取   語意   Embedding Chroma
      檢查   文字   切割              + MySQL
```

### 3. RAG 問答引擎

**功能**:
- 自然語言提問
- 語意檢索
- 上下文理解
- 多輪對話
- 來源追蹤

**RAG 流程**:
```
使用者提問
    ↓
1. 問題向量化（BGE-M3）
    ↓
2. 向量資料庫檢索（Chroma）
   - 相似度搜尋
   - 可選：過濾特定文件
    ↓
3. 取得前 K 個相關片段（Top-K Retrieval）
    ↓
4. 構建 Prompt
   - 系統指示
   - 相關上下文
   - 對話歷史
   - 使用者問題
    ↓
5. LLM 生成答案（Ollama）
    ↓
6. 解析答案和引用
    ↓
7. 儲存對話記錄
    ↓
8. 返回答案 + 來源
```

### 4. 對話管理

**功能**:
- 對話列表
- 多輪對話上下文
- 對話歷史
- 對話標題自動生成

**實作細節**:
```python
# 對話上下文管理
conversation = {
    "id": 1,
    "user_id": 1,
    "title": "關於 2023 年報的討論",
    "messages": [
        {"role": "user", "content": "這份年報的營收是多少？"},
        {"role": "assistant", "content": "根據第 5 頁..."},
        {"role": "user", "content": "去年相比呢？"},  # 記住上下文
        ...
    ]
}
```

### 5. 文件選擇機制

**功能**:
- 使用者可勾選要檢索的文件
- 只在選中的文件中搜尋答案
- 提高檢索精確度

**實作**:
```python
# 前端勾選
selected_docs = [1, 3, 5]  # 文件 ID

# 後端過濾
vectorstore.similarity_search(
    query=question,
    filter={
        "document_id": {"$in": selected_docs}
    }
)
```

## 資料流程詳解

### 文件上傳與處理

```
┌─────────────────────────────────────────────────────┐
│ 1. 使用者上傳文件（example.pdf）                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2. 後端驗證                                          │
│    - 檢查檔案大小（< 50MB）                          │
│    - 檢查檔案格式（PDF/Word/Excel/TXT）              │
│    - 檢查使用者權限                                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3. 儲存原始檔案                                      │
│    storage/documents/{user_id}/example.pdf          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4. 解析文件內容（Parser）                            │
│    - PDF: PyMuPDF (fitz)                            │
│    - Word: python-docx                              │
│    - Excel: openpyxl                                │
│    - TXT/MD: 直接讀取                                │
│    輸出: 純文字 + 元資料（頁碼、結構等）              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5. 語意分塊（Semantic Chunking）                    │
│    - 使用 RecursiveCharacterTextSplitter            │
│    - chunk_size: 500 字                             │
│    - chunk_overlap: 50 字（保持語意連貫）            │
│    - 保留文件結構資訊（章節、頁碼）                   │
│    輸出: [chunk1, chunk2, ...]                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 6. 向量化（Embedding）                               │
│    - 使用 BGE-M3 模型                                │
│    - 每個 chunk 轉換為 1024 維向量                   │
│    - 批次處理（提高效率）                             │
│    輸出: [vector1, vector2, ...]                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 7. 儲存到 Chroma                                     │
│    - 向量 + 原始文字 + 元資料                         │
│    - 元資料包含: document_id, page, chunk_index     │
│    storage/chroma_db/                               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 8. 更新 MySQL 文件表                                 │
│    - 文件名稱、大小、格式                            │
│    - 處理狀態: completed                             │
│    - chunk 數量                                      │
└─────────────────────────────────────────────────────┘
```

### 問答互動流程

```
┌─────────────────────────────────────────────────────┐
│ 1. 使用者輸入問題                                     │
│    「2023年的營收成長率是多少？」                      │
│    + 選擇文件範圍（可選）                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2. 問題向量化                                        │
│    - 使用相同的 BGE-M3 模型                          │
│    - 轉換為 1024 維向量                              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3. 向量檢索（Chroma）                                │
│    - 相似度搜尋（Cosine Similarity）                 │
│    - Top-K: 取前 5 個最相關片段                      │
│    - 應用過濾器（如果有選擇文件）                     │
│    輸出: [                                           │
│      {content: "...", metadata: {...}, score: 0.89},│
│      {content: "...", metadata: {...}, score: 0.85},│
│      ...                                            │
│    ]                                                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4. 構建 Prompt                                       │
│    system_prompt: "你是一個專業的文件分析助手..."      │
│    context: [檢索到的相關片段]                        │
│    history: [最近 3 輪對話]                          │
│    question: "2023年的營收成長率是多少？"             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5. LLM 生成答案（Ollama）                            │
│    - 呼叫 gpt-oss-20b 模型                           │
│    - 基於上下文生成答案                              │
│    - 標註引用來源                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 6. 解析答案                                          │
│    - 提取答案文字                                    │
│    - 提取引用來源（文件、頁碼）                       │
│    - 計算信心分數                                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 7. 儲存對話                                          │
│    - 問題和答案存入 messages 表                      │
│    - 更新 conversation 的 updated_at                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 8. 返回結果                                          │
│    {                                                │
│      "answer": "根據第12頁的數據...",                │
│      "sources": [                                   │
│        {"doc_id": 1, "page": 12, "content": "..."}  │
│      ],                                             │
│      "confidence": 0.87                             │
│    }                                                │
└─────────────────────────────────────────────────────┘
```

## 關鍵技術決策

### 為什麼使用 Ollama？

**相比 LM Studio**:
- ✅ **Docker 友善**: 官方提供 Docker 映像
- ✅ **AMD GPU 支援**: 透過 ROCm
- ✅ **API 標準**: OpenAI 相容介面
- ✅ **模型管理**: 簡單的 pull/push 機制
- ✅ **低耦合**: 輕鬆切換到 Gemini API

**設計模式**:
```python
# 抽象層，未來可無痛切換
class BaseLLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class OllamaService(BaseLLMService):
    def generate(self, prompt: str) -> str:
        # Ollama 實作
        pass

class GeminiService(BaseLLMService):
    def generate(self, prompt: str) -> str:
        # Gemini 實作
        pass

# 工廠模式選擇
llm = LLMFactory.create(settings.LLM_PROVIDER)
```

### 為什麼使用 BGE-M3？

- ✅ **中文效果優秀**: 專門針對中文優化
- ✅ **長文本支援**: 最長 8192 tokens
- ✅ **多語言**: 同時支援英文
- ✅ **開源**: 可本地部署
- ✅ **效能**: 在 CPU 上也能快速運行

### 為什麼使用 Chroma？

- ✅ **輕量級**: 純 Python，無外部依賴
- ✅ **易整合**: 與 LangChain 完美配合
- ✅ **功能完整**: 支援過濾、元資料查詢
- ✅ **持久化**: 可儲存到本地磁碟
- ✅ **效能**: 適合中小型應用（< 1M 文件）

### 語意分塊策略

**為什麼不用固定大小**:
- ❌ 可能切斷句子或段落
- ❌ 破壞語意完整性
- ❌ 降低檢索精確度

**為什麼用語意分塊**:
- ✅ 保持語意完整
- ✅ 按段落、句子分割
- ✅ 重疊區域保持上下文
- ✅ 更準確的相似度匹配

```python
# 語意分塊配置
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,              # 每塊約 500 字
    chunk_overlap=50,            # 重疊 50 字
    separators=["\n\n", "\n", "。", ". ", " "],  # 優先級
    keep_separator=True,         # 保留分隔符
    length_function=len          # 計算長度的函數
)
```

## 資料庫設計

### 資料持久化策略

```
┌─────────────────────────────────────────────┐
│ MySQL (Docker Volume 持久化)                │
│ - 使用者、群組、權限                         │
│ - 文件元資料                                 │
│ - 對話記錄                                   │
│ Volume: mysql_data                          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Chroma (宿主機目錄掛載)                      │
│ - 向量數據                                   │
│ - 文本片段                                   │
│ Path: ./storage/chroma_db/                  │
└─────────────────────────────────────────────┘

關聯方式: 透過 group_id 和 document_id
```

### 核心概念

**群組（Group）**:
- 文件的容器和組織單位
- 每個群組有獨立的 RAG 知識庫
- 支援多使用者協作

**權限等級**:
- `owner`: 群組擁有者（完整權限）
- `admin`: 管理員（可管理成員和文件）
- `editor`: 編輯者（可上傳和刪除文件）
- `viewer`: 檢視者（只能查看和問答）

### 使用者表（users）

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '使用者名稱',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '電子郵件',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密密碼',
    full_name VARCHAR(100) COMMENT '全名',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '系統角色',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='使用者資料表';
```

### 群組表（groups）

```sql
CREATE TABLE groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '群組名稱',
    description TEXT COMMENT '群組描述',
    owner_id INT NOT NULL COMMENT '擁有者 ID',

    -- 群組設定
    is_private BOOLEAN DEFAULT TRUE COMMENT '是否私有',
    allow_join_request BOOLEAN DEFAULT FALSE COMMENT '是否允許加入申請',

    -- 統計資訊
    member_count INT DEFAULT 1 COMMENT '成員數量',
    document_count INT DEFAULT 0 COMMENT '文件數量',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id),
    INDEX idx_name (name),
    INDEX idx_private (is_private)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組資料表';
```

### 群組成員表（group_members）

```sql
CREATE TABLE group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL COMMENT '群組 ID',
    user_id INT NOT NULL COMMENT '使用者 ID',

    -- 權限等級: owner > admin > editor > viewer
    role ENUM('owner', 'admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer' COMMENT '群組角色',

    -- 加入方式
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入時間',
    invited_by INT COMMENT '邀請者 ID',

    -- 狀態
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',

    UNIQUE KEY unique_group_user (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_group (group_id),
    INDEX idx_user (user_id),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組成員表';
```

### 文件表（documents）

```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL COMMENT '所屬群組 ID',
    uploader_id INT NOT NULL COMMENT '上傳者 ID',

    -- 檔案資訊
    filename VARCHAR(255) NOT NULL COMMENT '儲存檔名',
    original_filename VARCHAR(255) NOT NULL COMMENT '原始檔名',
    file_type VARCHAR(20) NOT NULL COMMENT '檔案類型: pdf/docx/xlsx/txt',
    file_size BIGINT NOT NULL COMMENT '檔案大小（bytes）',
    file_path VARCHAR(500) NOT NULL COMMENT '儲存路徑',

    -- 處理狀態
    processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '處理狀態',
    error_message TEXT COMMENT '錯誤訊息',

    -- 統計資訊
    chunk_count INT DEFAULT 0 COMMENT '切塊數量',
    page_count INT DEFAULT 0 COMMENT '頁數',

    -- 存取權限（繼承群組權限，可額外設定）
    min_view_role ENUM('owner', 'admin', 'editor', 'viewer') DEFAULT 'viewer' COMMENT '最低檢視權限',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_group (group_id),
    INDEX idx_uploader (uploader_id),
    INDEX idx_status (processing_status),
    INDEX idx_type (file_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件資料表';
```

### 對話表（conversations）

```sql
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '使用者 ID',
    group_id INT NOT NULL COMMENT '群組 ID（問答範圍）',
    title VARCHAR(200) COMMENT '對話標題（自動生成）',

    -- 統計資訊
    message_count INT DEFAULT 0 COMMENT '訊息數量',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_group (group_id),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='對話資料表';
```

### 訊息表（messages）

```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL COMMENT '對話 ID',
    role ENUM('user', 'assistant') NOT NULL COMMENT '角色',
    content TEXT NOT NULL COMMENT '訊息內容',

    -- 來源引用（JSON 格式）
    sources JSON COMMENT '來源引用',
    -- 格式: [{"doc_id": 1, "doc_name": "report.pdf", "page": 5, "chunk_index": 2, "content": "...", "score": 0.89}]

    -- 元資料
    token_count INT COMMENT 'Token 數量',
    generation_time FLOAT COMMENT '生成時間（秒）',
    model_used VARCHAR(50) COMMENT '使用的模型',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation (conversation_id),
    INDEX idx_role (role),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='訊息資料表';
```

### 資料表關係圖

```
users (使用者)
  │
  ├──► groups (擁有的群組)
  │      │
  │      ├──► documents (群組內的文件)
  │      │      │
  │      │      └──► Chroma Vector Store (向量數據)
  │      │
  │      └──► conversations (群組內的對話)
  │             │
  │             └──► messages (對話訊息)
  │
  └──► group_members (加入的群組)
         │
         └──► groups (可訪問的群組)
```

### 權限檢查邏輯

```python
# 範例：檢查使用者是否可以在群組中問答

def can_user_query_group(user_id: int, group_id: int) -> bool:
    """
    檢查使用者是否有權限在群組中問答

    業務邏輯：
    1. 查詢使用者在該群組的成員身份
    2. 任何群組成員（viewer 以上）都可以問答
    3. 但問答結果會根據使用者權限過濾文件

    Args:
        user_id: 使用者 ID
        group_id: 群組 ID

    Returns:
        bool: 是否有權限
    """
    # SQL 查詢
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.is_active == True
    ).first()

    return member is not None

def get_accessible_documents(user_id: int, group_id: int) -> List[int]:
    """
    取得使用者在群組中可訪問的文件 ID 列表

    業務邏輯：
    1. 查詢使用者的群組角色
    2. 根據角色過濾文件（min_view_role）
    3. 返回可訪問的文件 ID 列表

    權限層級（由高到低）：
    - owner: 可看所有文件
    - admin: 可看 admin/editor/viewer 級別的文件
    - editor: 可看 editor/viewer 級別的文件
    - viewer: 只能看 viewer 級別的文件

    Args:
        user_id: 使用者 ID
        group_id: 群組 ID

    Returns:
        List[int]: 可訪問的文件 ID 列表
    """
    # 查詢使用者角色
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()

    if not member:
        return []

    # 角色權限映射
    role_hierarchy = {
        'owner': ['owner', 'admin', 'editor', 'viewer'],
        'admin': ['admin', 'editor', 'viewer'],
        'editor': ['editor', 'viewer'],
        'viewer': ['viewer']
    }

    accessible_roles = role_hierarchy[member.role]

    # 查詢可訪問的文件
    documents = db.query(Document).filter(
        Document.group_id == group_id,
        Document.processing_status == 'completed',
        Document.min_view_role.in_(accessible_roles)
    ).all()

    return [doc.id for doc in documents]
```

## 開發階段規劃

### Phase 1: 基礎環境（當前）
- [x] 專案結構設計
- [ ] Docker 環境配置
- [ ] Ollama 安裝與測試
- [ ] MySQL 初始化
- [ ] 基礎文檔撰寫

### Phase 2: 核心功能
- [ ] 使用者認證系統
- [ ] 文件上傳 API
- [ ] 文件解析器（PDF/Word/Excel）
- [ ] RAG 基礎架構
- [ ] 前端基本框架

### Phase 3: RAG 整合
- [ ] Chroma 向量庫整合
- [ ] BGE-M3 Embedding
- [ ] Ollama LLM 整合
- [ ] 檢索鏈實作
- [ ] 對話管理

### Phase 4: 使用者介面
- [ ] 對話介面
- [ ] 文件管理頁面
- [ ] 來源引用顯示
- [ ] 文件選擇器
- [ ] 響應式設計

### Phase 5: 優化與測試
- [ ] 效能優化
- [ ] 錯誤處理
- [ ] 單元測試
- [ ] 整合測試
- [ ] 文檔完善

### Phase 6: 部署準備
- [ ] Docker 優化
- [ ] 環境變數管理
- [ ] 日誌系統
- [ ] 監控指標
- [ ] 部署文檔

## 注意事項

### 效能考量

- **Embedding 速度**: 約 1 秒/頁（取決於硬體）
- **LLM 推理**: 2-5 秒/回答（20B 模型）
- **向量檢索**: < 100ms（中小型資料庫）
- **並發支援**: 目前設計為 1-10 使用者
- **擴展方案**: 切換到 Gemini API 可支援更多並發

### 安全性考量

- **檔案驗證**: 檢查檔案類型和大小
- **路徑遍歷**: 防止 `../` 攻擊
- **SQL 注入**: 使用 ORM 參數化查詢
- **XSS 攻擊**: 前端過濾使用者輸入
- **權限控制**: 每個操作都檢查權限
- **敏感資訊**: 使用環境變數，不寫在程式碼中

### 資料安全

- **本地儲存**: 所有文件在 `storage/` 目錄
- **定期備份**: 建議定期備份 MySQL 和 `storage/`
- **權限隔離**: 每個使用者只能訪問自己的文件
- **日誌記錄**: 記錄所有重要操作

## 學習路徑建議

1. **Docker 基礎** → 理解容器化部署
2. **RAG 原理** → 理解檢索增強生成
3. **LangChain 使用** → 掌握 RAG 開發框架
4. **Ollama 操作** → 本地 LLM 運行
5. **向量資料庫** → Chroma 使用
6. **FastAPI 開發** → 後端 API 實作
7. **Vue 3 開發** → 前端介面建立

## 下一步

1. 閱讀 [Docker 環境設置](docs/02-docker-setup.md) 開始建立開發環境
2. 了解 [RAG 實作指南](docs/03-rag-implementation.md) 學習核心邏輯
3. 參考 [文件處理流程](docs/04-document-processing.md) 實作文件解析
4. 學習 [Ollama 整合](docs/05-ollama-integration.md) 串接 LLM

## 技術支援

- **LangChain 文檔**: https://python.langchain.com/
- **Ollama 文檔**: https://ollama.ai/
- **Chroma 文檔**: https://docs.trychroma.com/
- **FastAPI 文檔**: https://fastapi.tiangolo.com/
- **Vue 3 文檔**: https://vuejs.org/
