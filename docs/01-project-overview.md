# 01. 專案概述 - 圖書館 RAG Agent 系統

## 這個系統是什麼？

想像一下你有一個超級聰明的圖書館員助手，你可以：

1. **上傳文件**：把 PDF、Word、Excel 檔案丟給它
2. **問問題**：用自然語言問「這份報告的營收是多少？」
3. **得到答案**：它會翻找所有文件，找到相關段落，然後用自然語言回答你
4. **查看來源**：每個答案都附上引用來源（哪份文件、第幾頁）

**這就是 RAG (Retrieval-Augmented Generation) 系統！**

---

## 為什麼需要 RAG？

### 情境一：直接問 ChatGPT

你：「我們公司 2023 年 Q3 的營收是多少？」
ChatGPT：「抱歉，我無法取得您公司的內部資料...」

**問題**：ChatGPT 不知道你的私人文件內容。

### 情境二：使用我們的 RAG 系統

你：「我們公司 2023 年 Q3 的營收是多少？」
系統：
```
根據《2023年度財報.pdf》第 12 頁：
「2023年第三季度營收為新台幣 5,200 萬元，較去年同期成長 18%。」

來源：
📄 2023年度財報.pdf (第 12 頁)
```

**優勢**：
✅ 知道你的文件內容
✅ 答案有憑有據
✅ 可以追溯來源

---

## RAG 的運作原理（簡單版）

```
┌─────────────┐
│  1. 上傳文件  │  使用者上傳「年度報告.pdf」
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  2. 切成小塊  │  把 100 頁的文件切成 200 個小段落
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  3. 向量化   │  每個段落變成一串數字（向量）
│             │  例如: [0.23, -0.15, 0.87, ...]
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 4. 存入資料庫 │  儲存到 Chroma 向量資料庫
└─────────────┘

---

使用者提問：「營收是多少？」

┌─────────────┐
│ 5. 問題向量化 │  「營收是多少？」→ [0.25, -0.12, 0.91, ...]
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  6. 找相似段落 │  在資料庫中找最相似的 5 個段落
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  7. 餵給 LLM  │  把相關段落 + 問題一起給 LLM
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  8. 生成答案  │  LLM 根據段落內容回答問題
└─────────────┘
```

**關鍵概念**：
- **向量化**：把文字轉成數字，這樣電腦才能計算「相似度」
- **相似度搜尋**：找出和問題最相關的段落
- **上下文增強**：讓 LLM 基於真實文件回答，而非憑空想像

---

## 核心功能

### 1. 文件管理
- 上傳 PDF、Word、Excel、TXT/Markdown
- 自動解析和處理
- 檔案大小限制 50MB
- 處理狀態追蹤（處理中、完成、失敗）

### 2. 群組管理
- 建立群組作為文件的容器
- 邀請其他使用者加入群組
- 四種權限等級：
  - **Owner（擁有者）**：完全控制
  - **Admin（管理員）**：管理成員和文件
  - **Editor（編輯者）**：上傳和刪除文件
  - **Viewer（檢視者）**：只能查看和問答

### 3. 智能問答
- 用自然語言提問
- 支援多輪對話（記住上下文）
- 可選擇在特定文件中搜尋
- 每個答案都附上來源引用

### 4. 使用者認證
- 註冊和登入
- JWT Token 認證
- 密碼加密儲存

---

## 技術架構（簡單版）

```
┌─────────────────────────────────────────────┐
│              使用者（瀏覽器）                  │
│         http://localhost:5173                │
└────────────────┬────────────────────────────┘
                 │
                 │ Vue 3 前端
                 │ (Vite + TypeScript + Tailwind)
                 │
┌────────────────▼────────────────────────────┐
│              API 層 (FastAPI)                │
│         http://localhost:8000                │
│                                              │
│  /api/auth/login        登入                 │
│  /api/documents/upload  上傳文件             │
│  /api/chat/ask          問答                 │
└───┬──────────┬──────────┬─────────┬─────────┘
    │          │          │         │
    │          │          │         │
┌───▼────┐ ┌──▼─────┐ ┌──▼──────┐ ┌▼────────┐
│ MySQL  │ │ Chroma │ │ Ollama  │ │ Storage │
│        │ │        │ │         │ │         │
│ 使用者  │ │ 向量   │ │ LLM     │ │ 檔案    │
│ 群組   │ │ 資料庫 │ │ 模型    │ │ 儲存    │
│ 權限   │ │        │ │         │ │         │
└────────┘ └────────┘ └─────────┘ └─────────┘
```

---

## 為什麼選擇這些技術？

### 前端：Vue 3 + TypeScript

**Vue 3**：
- 簡單易學，適合快速開發
- 響應式資料綁定（資料改變，畫面自動更新）
- 組件化開發（像樂高一樣組裝介面）

**TypeScript**：
- 型別檢查，減少錯誤
- 更好的開發體驗（自動完成）

**Tailwind CSS**：
- 快速寫樣式
- 一致的設計系統

### 後端：FastAPI

**為什麼不用 Flask/Django？**

| 特性 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 效能 | ⚡⚡⚡ | ⚡ | ⚡⚡ |
| 非同步 | ✅ | ❌ | 部分支援 |
| 型別提示 | ✅ | ❌ | ❌ |
| 自動文件 | ✅ | ❌ | ❌ |
| 學習曲線 | 中等 | 簡單 | 複雜 |

**FastAPI 優勢**：
- 原生支援非同步（處理多個請求不會卡住）
- 自動生成 API 文件（http://localhost:8000/docs）
- 型別檢查（減少錯誤）
- 內建 WebSocket（未來做即時對話）

### 資料庫：MySQL 8.0

**為什麼不用 PostgreSQL？**
- MySQL 更普及，學習資源多
- 效能足夠（中小型應用）
- JSON 欄位支援（儲存來源引用）

**儲存內容**：
- 使用者資料
- 群組和權限
- 文件元資料（檔名、大小、狀態）
- 對話記錄

### 向量資料庫：Chroma

**什麼是向量資料庫？**
普通資料庫：搜尋「完全相符」的文字
向量資料庫：搜尋「語意相似」的內容

例如：
- 問「營收」→ 能找到「收入」、「業績」
- 問「如何提升效率」→ 能找到「改善流程」、「優化方法」

**為什麼選 Chroma？**
- 輕量級（純 Python，無外部依賴）
- 與 LangChain 整合良好
- 支援過濾（只在特定文件中搜尋）
- 持久化儲存（資料不會遺失）

### LLM：Ollama + gpt-oss-20b

**為什麼用 Ollama？**
- 本地運行（資料不外傳，隱私安全）
- 支援 AMD GPU（透過 ROCm）
- Docker 友善（易於部署）
- 與 OpenAI API 相容（未來可切換）

**為什麼用 gpt-oss-20b？**
- 20B 參數（效果好，又不會太大）
- 中英文支援良好
- 16GB VRAM 可運行（量化版）

**低耦合設計**：
```python
# 抽象層 - 未來可無痛切換到 Gemini API
class BaseLLMService:
    def generate(self, prompt: str) -> str:
        pass

class OllamaService(BaseLLMService):
    def generate(self, prompt: str) -> str:
        # Ollama 實作
        pass

class GeminiService(BaseLLMService):
    def generate(self, prompt: str) -> str:
        # Gemini 實作（未來）
        pass
```

### Embedding 模型：BGE-M3

**什麼是 Embedding？**
把文字轉成向量（數字陣列），用來計算相似度。

**為什麼選 BGE-M3？**
- 中文效果優秀（BAAI 針對中文優化）
- 支援長文本（最長 8192 tokens）
- 多語言（中英文通用）
- 開源（可本地運行）

---

## 專案目錄結構（重點說明）

```
library_agent/
│
├── frontend/               # 前端 Vue 應用
│   ├── src/
│   │   ├── components/    # UI 組件
│   │   ├── views/         # 頁面
│   │   ├── stores/        # 狀態管理（Pinia）
│   │   └── services/      # API 呼叫
│   └── package.json
│
├── backend/                # 後端 FastAPI 應用
│   ├── app/
│   │   ├── models/        # 資料庫模型（對應 MySQL 表格）
│   │   ├── schemas/       # 資料驗證（Pydantic）
│   │   ├── services/      # 業務邏輯
│   │   │   ├── llm/       # LLM 服務（Ollama/Gemini）
│   │   │   ├── rag/       # RAG 核心邏輯
│   │   │   └── document/  # 文件處理
│   │   ├── api/           # API 路由
│   │   └── core/          # 核心配置
│   └── requirements.txt
│
├── storage/                # 本地儲存（不提交到 Git）
│   ├── documents/         # 原始文件
│   ├── chroma_db/         # Chroma 向量資料庫
│   └── ollama/            # Ollama 模型
│
├── docker/                 # Docker 配置
│   ├── mysql/init.sql     # 資料庫初始化
│   ├── backend/Dockerfile
│   └── frontend/Dockerfile
│
├── docs/                   # 教學文件（你現在在這裡！）
│
├── docker-compose.yml      # 服務編排
├── .env.example           # 環境變數範例
└── README.md              # 專案說明
```

**重要資料夾說明**：

### backend/app/services/
這是業務邏輯的核心，分成三大塊：

1. **llm/** - LLM 服務
   - `base.py`: 抽象基類（定義介面）
   - `ollama_service.py`: Ollama 實作
   - `factory.py`: 工廠模式（選擇使用哪個 LLM）

2. **rag/** - RAG 核心
   - `embedder.py`: Embedding 服務（文字轉向量）
   - `vectorstore.py`: Chroma 操作（儲存和檢索向量）
   - `retriever.py`: 檢索策略（如何找相關段落）
   - `chain.py`: RAG Chain（組裝完整流程）

3. **document/** - 文件處理
   - `parser.py`: 解析各種格式（PDF/Word/Excel）
   - `chunker.py`: 語意分塊
   - `processor.py`: 協調處理流程

### storage/
這個資料夾存放實際的檔案和資料：

- **documents/**: 使用者上傳的原始檔案
  ```
  storage/documents/
  ├── user_1/
  │   ├── abc123.pdf
  │   └── def456.docx
  └── user_2/
      └── xyz789.xlsx
  ```

- **chroma_db/**: Chroma 的向量資料和索引
  ```
  storage/chroma_db/
  ├── chroma.sqlite3      # Chroma 的 metadata
  ├── index/              # 向量索引
  └── ...
  ```

- **ollama/**: Ollama 下載的模型檔案
  ```
  storage/ollama/
  └── models/
      └── gpt-oss-20b/    # 約 10-20GB
  ```

---

## 資料流程總覽

### 文件上傳流程

```
使用者選擇檔案（report.pdf）
    ↓
前端驗證（大小、格式）
    ↓
POST /api/documents/upload
    ↓
後端接收檔案
    ↓
1. 儲存到 storage/documents/{user_id}/abc123.pdf
2. 寫入 MySQL (documents 表)
    - filename: abc123.pdf
    - original_filename: report.pdf
    - processing_status: pending
    ↓
背景任務開始處理：
    ↓
3. 解析 PDF → 提取文字
4. 語意分塊 → 200 個 chunks
5. Embedding → 每個 chunk 轉成 1024 維向量
6. 存入 Chroma
    - 向量 + 原始文字 + metadata
    ↓
7. 更新 MySQL
    - processing_status: completed
    - chunk_count: 200
    ↓
完成！使用者可以開始問答
```

### 問答流程

```
使用者輸入：「2023年營收是多少？」
    ↓
POST /api/chat/ask
{
  "question": "2023年營收是多少？",
  "conversation_id": 1,
  "document_ids": [1, 2]  // 只在這些文件中搜尋（可選）
}
    ↓
1. 檢查權限
   - 使用者是否有權訪問這些文件？
    ↓
2. 問題向量化
   - "2023年營收是多少？" → [0.25, -0.12, 0.91, ...]
    ↓
3. Chroma 相似度搜尋
   - 找出最相關的 5 個 chunks
   - 結果範例：
     [
       {content: "2023年營收...", score: 0.89, doc_id: 1, page: 5},
       {content: "較去年成長...", score: 0.85, doc_id: 1, page: 6},
       ...
     ]
    ↓
4. 建構 Prompt
   system: "你是專業的文件分析助手..."
   context: [檢索到的 5 個段落]
   history: [最近 3 輪對話]
   question: "2023年營收是多少？"
    ↓
5. 呼叫 Ollama LLM
   - 生成答案
    ↓
6. 解析答案和來源
    ↓
7. 儲存到 MySQL (messages 表)
    ↓
8. 返回給前端
{
  "answer": "根據文件顯示...",
  "sources": [
    {
      "doc_id": 1,
      "doc_name": "report.pdf",
      "page": 5,
      "content": "...",
      "score": 0.89
    }
  ]
}
    ↓
前端顯示答案 + 來源引用
```

---

## 權限設計（重要！）

### 四種角色

```
Owner（擁有者）
  ├─ 管理群組設定
  ├─ 新增/移除成員
  ├─ 修改成員權限
  ├─ 上傳/刪除文件
  ├─ 查看和問答
  └─ 刪除群組

Admin（管理員）
  ├─ 新增/移除成員
  ├─ 上傳/刪除文件
  ├─ 查看和問答
  └─ ❌ 無法刪除群組

Editor（編輯者）
  ├─ 上傳/刪除文件
  ├─ 查看和問答
  └─ ❌ 無法管理成員

Viewer（檢視者）
  ├─ 查看和問答
  └─ ❌ 無法上傳文件
```

### 文件層級權限

每個文件可設定 `min_view_role`（最低可查看角色）：

**範例**：
```
群組「財務部」：
  - Alice: owner
  - Bob: admin
  - Carol: viewer

文件「敏感財報.pdf」：
  - min_view_role: admin

結果：
  ✅ Alice 可以看（owner ≥ admin）
  ✅ Bob 可以看（admin ≥ admin）
  ❌ Carol 不能看（viewer < admin）
```

### 權限檢查流程

```python
def can_user_view_document(user_id: int, doc_id: int) -> bool:
    """檢查使用者是否可以查看文件"""

    # 1. 取得文件資訊
    doc = db.query(Document).filter(Document.id == doc_id).first()

    # 2. 取得使用者在該群組的角色
    member = db.query(GroupMember).filter(
        GroupMember.group_id == doc.group_id,
        GroupMember.user_id == user_id
    ).first()

    if not member:
        return False  # 不是群組成員

    # 3. 檢查角色是否足夠
    role_hierarchy = ['viewer', 'editor', 'admin', 'owner']
    user_level = role_hierarchy.index(member.role)
    required_level = role_hierarchy.index(doc.min_view_role)

    return user_level >= required_level
```

---

## 與其他系統的比較

### vs. Google Drive + ChatGPT

| 功能 | 我們的系統 | Google Drive + ChatGPT |
|------|------------|------------------------|
| 文件儲存 | ✅ | ✅ |
| 智能問答 | ✅ | ❌（ChatGPT 看不到你的 Drive）|
| 來源追蹤 | ✅ | ❌ |
| 資料隱私 | ✅（本地） | ❌（上傳到 OpenAI）|
| 成本 | 免費（自己主機） | 每月訂閱 |

### vs. Notion AI

| 功能 | 我們的系統 | Notion AI |
|------|------------|-----------|
| 支援格式 | PDF/Word/Excel | 主要是文字 |
| 本地部署 | ✅ | ❌ |
| 客製化 | ✅ | ❌ |
| 群組權限 | 細緻控制 | 基本權限 |
| 成本 | 免費 | 每月 $10/人 |

### vs. 企業搜尋系統（如 Elasticsearch）

| 功能 | RAG 系統 | Elasticsearch |
|------|----------|---------------|
| 關鍵字搜尋 | ✅ | ✅ |
| 語意搜尋 | ✅ | ❌ |
| 自然語言回答 | ✅ | ❌（只返回文件）|
| 學習曲線 | 中等 | 複雜 |

---

## 適用場景

### ✅ 適合

1. **企業內部知識庫**
   - 公司規章、SOP、技術文件
   - 只有內部員工可訪問

2. **研究團隊**
   - 論文、研究報告
   - 快速查找相關資訊

3. **法律/醫療文件管理**
   - 大量專業文件
   - 需要精確引用來源

4. **客服知識庫**
   - 產品說明、FAQ
   - 快速找到答案

### ❌ 不適合

1. **即時協作編輯**
   - 用 Google Docs / Notion

2. **超大規模（百萬文件）**
   - 需要更強大的向量資料庫（如 Milvus、Weaviate）

3. **需要精確的表格運算**
   - 用 Excel / 資料庫

---

## 效能考量

### 硬體需求

**最低配置**（CPU 運行）：
- CPU: 4 核心
- RAM: 8GB
- 硬碟: 50GB
- **速度**: 慢（5-10 秒/回答）

**建議配置**（GPU 加速）：
- CPU: 8 核心
- RAM: 16GB
- GPU: 8GB VRAM（AMD/NVIDIA）
- 硬碟: 100GB
- **速度**: 快（2-3 秒/回答）

**最佳配置**（生產環境）：
- CPU: 16 核心
- RAM: 32GB
- GPU: 16GB VRAM
- 硬碟: 500GB SSD
- **速度**: 很快（1-2 秒/回答）

### 擴展性

**目前設計支援**：
- 1-10 並發使用者
- < 10,000 文件
- < 1TB 儲存

**未來擴展方案**：
- 切換到 Gemini API（雲端 LLM）→ 支援更多並發
- 升級到 Milvus/Weaviate（雲端向量庫）→ 支援更多文件
- 加入 Redis 快取 → 提升回應速度

---

## 安全性設計

### 1. 認證安全
- 密碼使用 bcrypt 加密（不可逆）
- JWT Token 有效期限（預設 30 分鐘）
- Refresh Token 機制（未來）

### 2. 資料隔離
- 每個使用者只能訪問其群組的文件
- 檔案按 user_id 分資料夾儲存
- 向量資料包含 group_id 過濾

### 3. 檔案安全
- 檔案類型白名單（只允許 PDF/Word/Excel/TXT）
- 檔案大小限制（50MB）
- 檔名使用 UUID（防止路徑遍歷）

### 4. API 安全
- CORS 限制（只允許特定來源）
- Rate Limiting（防止 DDoS）
- 輸入驗證（Pydantic）

---

## 開發階段規劃

### Phase 1: 基礎環境 ✅（已完成）
- [x] 專案結構設計
- [x] Docker 環境配置
- [x] MySQL 初始化
- [x] 教學文件撰寫

### Phase 2: 核心功能（預計 1 週）
- [ ] 使用者認證 API
- [ ] 文件上傳 API
- [ ] 文件解析器
- [ ] RAG 基礎架構

### Phase 3: RAG 整合（預計 1 週）
- [ ] Chroma 整合
- [ ] BGE-M3 Embedding
- [ ] Ollama LLM 整合
- [ ] 檢索鏈實作

### Phase 4: 前端介面（預計 1 週）
- [ ] 登入/註冊頁面
- [ ] 文件管理頁面
- [ ] 對話介面
- [ ] 來源引用顯示

### Phase 5: 優化測試（預計 3 天）
- [ ] 效能優化
- [ ] 錯誤處理
- [ ] 單元測試
- [ ] 整合測試

---

## 常見問題

### Q1: 我完全不懂 AI/ML，能學會嗎？
**A**: 可以！這個專案不需要你懂 AI 的數學原理。我們把 AI 當作「黑盒子」工具來用，重點是理解「輸入什麼」和「輸出什麼」。

### Q2: 一定要有 GPU 嗎？
**A**: 不一定。CPU 也能跑，只是比較慢（5-10 秒/回答）。如果只是學習和測試，CPU 就夠了。

### Q3: 可以用 OpenAI API 嗎？
**A**: 可以！我們的設計是低耦合的，只要實作 `BaseLLMService` 介面，就能輕鬆切換到 OpenAI、Gemini 或其他 LLM。

### Q4: 資料會外洩嗎？
**A**: 不會。所有資料都在你的主機上（本地 LLM、本地資料庫、本地檔案）。除非你主動開放外網訪問。

### Q5: 支援中文嗎？
**A**: 完全支援！我們特別選用 BGE-M3（中文優化）和 gpt-oss-20b（支援中文）。

### Q6: 可以商用嗎？
**A**: 可以，但要注意：
- gpt-oss-20b 的授權條款
- 確保你的使用符合開源協議
- 建議諮詢法律顧問

---

## 下一步

現在你已經了解整個系統的全貌，接下來：

1. **實際操作**：前往 [02. Docker 環境設置](02-docker-environment.md) 開始建立環境
2. **深入理解**：閱讀 [04. RAG 基礎原理](04-rag-fundamentals.md) 理解核心技術
3. **動手實作**：跟著 [08. 後端實作指南](08-backend-implementation.md) 寫程式

---

## 學習資源

### 影片教學
- [RAG 是什麼？5 分鐘看懂](https://www.youtube.com/watch?v=...)
- [向量資料庫入門](https://www.youtube.com/watch?v=...)

### 延伸閱讀
- [LangChain RAG 教學](https://python.langchain.com/docs/use_cases/question_answering/)
- [Ollama 官方文件](https://ollama.ai/)
- [Chroma 快速入門](https://docs.trychroma.com/getting-started)

### 範例專案
- [LangChain 官方 RAG 範例](https://github.com/langchain-ai/langchain/tree/master/templates)
- [Chroma 使用範例](https://github.com/chroma-core/chroma)

---

**準備好了嗎？讓我們開始建立環境吧！→ [02. Docker 環境設置](02-docker-environment.md)**
