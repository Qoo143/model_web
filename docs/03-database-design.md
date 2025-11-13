# 03. 資料庫設計 - 多使用者、多群組架構

## 資料庫是什麼？（用比喻理解）

想像一個圖書館的管理系統：

```
傳統方式（Excel 檔案）：
📊 users.xlsx       - 使用者資料
📊 documents.xlsx   - 文件清單
📊 groups.xlsx      - 群組資訊

問題：
❌ 如何確保「文件」一定屬於某個「群組」？
❌ 如何快速找到「Alice 有權限的所有文件」？
❌ 多人同時修改會衝突

資料庫方式（MySQL）：
🗄️ 結構化儲存
🔗 資料表之間有關聯
⚡ 快速查詢
🔒 交易保證（多人存取安全）
```

---

## 為什麼需要這些資料表？

### 核心需求分析

我們的系統需要：

1. **多使用者**：很多人使用系統
2. **多群組**：每個人可以建立多個群組
3. **權限控制**：不同人對群組有不同權限
4. **文件管理**：文件屬於群組，有處理狀態
5. **對話記錄**：保存問答歷史

### 資料表設計策略

```
users (使用者)
  ↓ 擁有
groups (群組)
  ↓ 包含
documents (文件)

users (使用者)
  ↓ 加入
group_members (成員關聯)
  ↓ 連接
groups (群組)

users (使用者)
  ↓ 發起
conversations (對話)
  ↓ 包含
messages (訊息)
```

---

## 資料表關聯圖（ER Diagram）

```
┌─────────────┐
│   users     │
│ (使用者)     │
├─────────────┤
│ id (PK)     │◄───┐
│ username    │    │
│ email       │    │
│ password    │    │
│ role        │    │
└─────────────┘    │
       │           │
       │ 擁有       │
       │           │
       ▼           │
┌─────────────┐    │
│   groups    │    │
│ (群組)       │    │
├─────────────┤    │
│ id (PK)     │◄───┼───┐
│ name        │    │   │
│ owner_id(FK)├────┘   │
│ description │        │
└─────────────┘        │
       │               │
       │ 包含           │
       │               │
       ▼               │
┌──────────────┐       │
│  documents   │       │
│ (文件)        │       │
├──────────────┤       │
│ id (PK)      │       │
│ filename     │       │
│ group_id (FK)├───────┘
│ status       │
└──────────────┘

┌──────────────────┐
│ group_members    │
│ (成員關聯)        │
├──────────────────┤
│ id (PK)          │
│ group_id (FK)    ├─────► groups
│ user_id (FK)     ├─────► users
│ role             │
└──────────────────┘
```

**關鍵關聯**：
- `groups.owner_id` → `users.id`：誰建立這個群組
- `documents.group_id` → `groups.id`：文件屬於哪個群組
- `group_members.group_id` → `groups.id`：成員在哪個群組
- `group_members.user_id` → `users.id`：哪個使用者

---

## 資料表詳解

### 1. users (使用者表)

**用途**：儲存所有使用者的基本資料

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    department VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**欄位說明**：

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `id` | INT | 主鍵（唯一識別碼） | 1, 2, 3... |
| `username` | VARCHAR(50) | 使用者名稱（唯一） | alice, bob |
| `email` | VARCHAR(100) | 電子郵件（唯一） | alice@example.com |
| `hashed_password` | VARCHAR(255) | 加密後的密碼 | $2b$12$... |
| `role` | ENUM | 系統角色 | 'user', 'admin' |
| `department` | VARCHAR(50) | 部門（選填） | '財務部', '研發部' |
| `is_active` | BOOLEAN | 帳號是否啟用 | TRUE, FALSE |
| `created_at` | DATETIME | 建立時間 | 2024-01-15 10:30:00 |
| `updated_at` | DATETIME | 最後更新時間 | 2024-03-20 14:22:10 |

**索引**：
- `PRIMARY KEY (id)`：主鍵索引
- `UNIQUE (username)`：確保使用者名稱不重複
- `UNIQUE (email)`：確保郵件不重複
- `INDEX (username)`：加速使用者名稱查詢

**範例資料**：

```sql
INSERT INTO users (username, email, hashed_password, role) VALUES
('alice', 'alice@company.com', '$2b$12$abc...', 'admin'),
('bob', 'bob@company.com', '$2b$12$def...', 'user'),
('carol', 'carol@company.com', '$2b$12$ghi...', 'user');
```

**為什麼要 hashed_password 而不是 password？**
- 資料庫被駭，密碼也不會外洩
- 使用 bcrypt 加密（單向加密，無法反推）
- 驗證時比對加密後的結果

---

### 2. groups (群組表)

**用途**：文件的容器，多人協作的單位

```sql
CREATE TABLE groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    is_private BOOLEAN DEFAULT TRUE,
    allow_join_request BOOLEAN DEFAULT FALSE,
    member_count INT DEFAULT 1,
    document_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**欄位說明**：

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `id` | INT | 主鍵 | 1, 2, 3... |
| `name` | VARCHAR(100) | 群組名稱 | '財務部文件庫' |
| `description` | TEXT | 群組描述 | '存放年度財報...' |
| `owner_id` | INT | 擁有者 ID (外鍵) | 1 (指向 users.id) |
| `is_private` | BOOLEAN | 是否為私有群組 | TRUE (只有成員可見) |
| `allow_join_request` | BOOLEAN | 是否允許申請加入 | FALSE |
| `member_count` | INT | 成員數量 | 5 |
| `document_count` | INT | 文件數量 | 23 |
| `created_at` | DATETIME | 建立時間 | 2024-01-15 10:30:00 |
| `updated_at` | DATETIME | 最後更新時間 | 2024-03-20 14:22:10 |

**外鍵約束**：
```sql
FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
```

**解釋**：
- `owner_id` 必須是 `users` 表中存在的 `id`
- `ON DELETE CASCADE`：如果使用者被刪除，其擁有的群組也會被刪除

**範例資料**：

```sql
INSERT INTO groups (name, description, owner_id, is_private) VALUES
('我的文件庫', '個人文件管理', 1, TRUE),
('財務部', '財務相關文件', 1, FALSE),
('研發部知識庫', '技術文件共享', 2, FALSE);
```

---

### 3. group_members (群組成員表)

**用途**：連接使用者和群組，並定義權限

```sql
CREATE TABLE group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('owner', 'admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    invited_by INT,
    is_active BOOLEAN DEFAULT TRUE,

    UNIQUE KEY unique_group_user (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL
);
```

**欄位說明**：

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `id` | INT | 主鍵 | 1, 2, 3... |
| `group_id` | INT | 群組 ID (外鍵) | 1 |
| `user_id` | INT | 使用者 ID (外鍵) | 2 |
| `role` | ENUM | 群組角色 | 'admin' |
| `joined_at` | DATETIME | 加入時間 | 2024-01-15 10:30:00 |
| `invited_by` | INT | 邀請者 ID | 1 |
| `is_active` | BOOLEAN | 是否為活躍成員 | TRUE |

**權限層級**：

```
owner (擁有者)
  ├─ 刪除群組
  ├─ 修改群組設定
  ├─ 新增/移除成員
  ├─ 修改成員權限
  ├─ 上傳/刪除文件
  └─ 查看和問答

admin (管理員)
  ├─ 新增/移除成員
  ├─ 上傳/刪除文件
  └─ 查看和問答

editor (編輯者)
  ├─ 上傳/刪除文件
  └─ 查看和問答

viewer (檢視者)
  └─ 查看和問答
```

**唯一約束**：
```sql
UNIQUE KEY unique_group_user (group_id, user_id)
```
**解釋**：同一個使用者在同一個群組中只能有一個角色

**範例資料**：

```sql
-- Alice 是「財務部」的 owner
INSERT INTO group_members (group_id, user_id, role) VALUES (2, 1, 'owner');

-- Bob 是「財務部」的 admin
INSERT INTO group_members (group_id, user_id, role, invited_by) VALUES (2, 2, 'admin', 1);

-- Carol 是「財務部」的 viewer
INSERT INTO group_members (group_id, user_id, role, invited_by) VALUES (2, 3, 'viewer', 1);
```

---

### 4. documents (文件表)

**用途**：儲存文件的元資料（實際檔案在 storage/）

```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size BIGINT NOT NULL,
    file_path VARCHAR(500) NOT NULL,

    group_id INT NOT NULL,
    uploaded_by INT NOT NULL,

    min_view_role ENUM('owner', 'admin', 'editor', 'viewer') DEFAULT 'viewer',

    processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    error_message TEXT,

    chunk_count INT DEFAULT 0,
    page_count INT DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);
```

**欄位說明**：

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `id` | INT | 主鍵 | 1 |
| `filename` | VARCHAR(255) | 儲存的檔名 (UUID) | 'abc-123.pdf' |
| `original_filename` | VARCHAR(255) | 原始檔名 | '2023年報.pdf' |
| `file_type` | VARCHAR(20) | 檔案類型 | 'pdf', 'docx' |
| `file_size` | BIGINT | 檔案大小 (bytes) | 5242880 (5MB) |
| `file_path` | VARCHAR(500) | 儲存路徑 | 'user_1/abc-123.pdf' |
| `group_id` | INT | 所屬群組 | 2 |
| `uploaded_by` | INT | 上傳者 | 1 |
| `min_view_role` | ENUM | 最低可查看權限 | 'viewer' |
| `processing_status` | ENUM | 處理狀態 | 'completed' |
| `error_message` | TEXT | 錯誤訊息 | NULL |
| `chunk_count` | INT | 切塊數量 | 150 |
| `page_count` | INT | 頁數 | 75 |

**處理狀態流程**：

```
pending (等待處理)
    ↓
processing (處理中)
    ↓
completed (完成) 或 failed (失敗)
```

**範例資料**：

```sql
INSERT INTO documents (
    filename, original_filename, file_type, file_size, file_path,
    group_id, uploaded_by, processing_status, chunk_count, page_count
) VALUES (
    'abc-123-456.pdf',
    '2023年度財報.pdf',
    'pdf',
    5242880,
    'user_1/abc-123-456.pdf',
    2,
    1,
    'completed',
    150,
    75
);
```

---

### 5. conversations (對話表)

**用途**：一次完整的對話會話

```sql
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    title VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);
```

**欄位說明**：

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `id` | INT | 主鍵 | 1 |
| `user_id` | INT | 使用者 ID | 1 |
| `group_id` | INT | 群組 ID（問答範圍） | 2 |
| `title` | VARCHAR(200) | 對話標題 | '關於2023年報的討論' |
| `created_at` | DATETIME | 建立時間 | 2024-03-20 10:00:00 |
| `updated_at` | DATETIME | 最後更新時間 | 2024-03-20 11:30:00 |

**為什麼需要 group_id？**
- 對話範圍限定在特定群組
- 只會檢索該群組的文件
- 權限檢查時使用

**標題如何生成？**
```python
# 方法 1: 使用第一個問題
title = first_message.content[:50]  # "2023年營收是多少？"

# 方法 2: 讓 LLM 生成摘要
title = llm.generate("為這段對話生成標題: ...")  # "關於2023年報的討論"
```

---

### 6. messages (訊息表)

**用途**：儲存對話中的每一條訊息

```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,

    sources JSON,

    token_count INT,
    generation_time FLOAT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);
```

**欄位說明**：

| 欄位 | 型別 | 說明 | 範例 |
|------|------|------|------|
| `id` | INT | 主鍵 | 1 |
| `conversation_id` | INT | 所屬對話 | 1 |
| `role` | ENUM | 角色 | 'user', 'assistant' |
| `content` | TEXT | 訊息內容 | '2023年營收是多少？' |
| `sources` | JSON | 來源引用 | (見下方) |
| `token_count` | INT | Token 數量 | 150 |
| `generation_time` | FLOAT | 生成時間 (秒) | 2.5 |

**sources JSON 格式**：

```json
[
  {
    "doc_id": 1,
    "doc_name": "2023年報.pdf",
    "page": 12,
    "chunk_index": 5,
    "content": "2023年第三季度營收為新台幣 5,200 萬元...",
    "score": 0.89
  },
  {
    "doc_id": 1,
    "doc_name": "2023年報.pdf",
    "page": 13,
    "chunk_index": 6,
    "content": "較去年同期成長 18%...",
    "score": 0.85
  }
]
```

**範例資料**：

```sql
-- 使用者提問
INSERT INTO messages (conversation_id, role, content) VALUES
(1, 'user', '2023年營收是多少？');

-- AI 回答
INSERT INTO messages (
    conversation_id, role, content, sources, token_count, generation_time
) VALUES (
    1,
    'assistant',
    '根據《2023年度財報》第12頁，2023年第三季度營收為新台幣 5,200 萬元，較去年同期成長 18%。',
    '[{"doc_id": 1, "doc_name": "2023年報.pdf", "page": 12, "score": 0.89}]',
    45,
    2.3
);
```

---

## 資料表關聯實例

### 情境：Alice 建立財務部群組並邀請 Bob

```sql
-- 1. Alice 建立群組
INSERT INTO groups (name, owner_id) VALUES ('財務部', 1);
-- group_id = 2

-- 2. Alice 自動成為 owner
INSERT INTO group_members (group_id, user_id, role) VALUES (2, 1, 'owner');

-- 3. Alice 邀請 Bob 成為 admin
INSERT INTO group_members (group_id, user_id, role, invited_by)
VALUES (2, 2, 'admin', 1);

-- 4. 更新群組成員數
UPDATE groups SET member_count = 2 WHERE id = 2;
```

### 情境：Bob 上傳文件到財務部

```sql
-- 1. 儲存文件元資料
INSERT INTO documents (
    filename, original_filename, file_type, file_size, file_path,
    group_id, uploaded_by, processing_status
) VALUES (
    'xyz-789.pdf', '2023Q3報表.pdf', 'pdf', 3145728, 'user_2/xyz-789.pdf',
    2, 2, 'pending'
);
-- document_id = 3

-- 2. 背景處理完成後更新狀態
UPDATE documents
SET processing_status = 'completed', chunk_count = 80, page_count = 40
WHERE id = 3;

-- 3. 更新群組文件數
UPDATE groups SET document_count = document_count + 1 WHERE id = 2;
```

### 情境：Carol 加入財務部並開始對話

```sql
-- 1. Alice 邀請 Carol 成為 viewer
INSERT INTO group_members (group_id, user_id, role, invited_by)
VALUES (2, 3, 'viewer', 1);

-- 2. Carol 建立新對話
INSERT INTO conversations (user_id, group_id, title)
VALUES (3, 2, '查詢Q3營收');
-- conversation_id = 1

-- 3. Carol 提問
INSERT INTO messages (conversation_id, role, content)
VALUES (1, 'user', 'Q3營收是多少？');

-- 4. 系統回答
INSERT INTO messages (conversation_id, role, content, sources)
VALUES (
    1,
    'assistant',
    '根據文件...',
    '[{"doc_id": 3, "page": 5, "score": 0.92}]'
);
```

---

## SQL 查詢實例

### 查詢 1: 取得使用者有權限的所有群組

```sql
SELECT
    g.id,
    g.name,
    g.description,
    gm.role AS my_role,
    g.member_count,
    g.document_count
FROM groups g
INNER JOIN group_members gm ON g.id = gm.group_id
WHERE gm.user_id = 1  -- Alice 的 ID
  AND gm.is_active = TRUE
ORDER BY g.updated_at DESC;
```

**結果**：
```
id | name     | description      | my_role | member_count | document_count
---|----------|------------------|---------|--------------|---------------
2  | 財務部    | 財務相關文件      | owner   | 3            | 5
1  | 我的文件庫 | 個人文件管理      | owner   | 1            | 10
```

### 查詢 2: 取得群組內使用者可查看的文件

```sql
SELECT
    d.id,
    d.original_filename,
    d.file_type,
    d.file_size,
    d.processing_status,
    d.chunk_count,
    u.username AS uploader
FROM documents d
INNER JOIN users u ON d.uploaded_by = u.id
INNER JOIN group_members gm ON d.group_id = gm.group_id
WHERE d.group_id = 2  -- 財務部
  AND gm.user_id = 3  -- Carol
  AND d.processing_status = 'completed'
  -- 權限檢查: Carol 的角色是否足夠
  AND (
    (gm.role = 'owner') OR
    (gm.role = 'admin' AND d.min_view_role IN ('admin', 'editor', 'viewer')) OR
    (gm.role = 'editor' AND d.min_view_role IN ('editor', 'viewer')) OR
    (gm.role = 'viewer' AND d.min_view_role = 'viewer')
  )
ORDER BY d.created_at DESC;
```

### 查詢 3: 取得對話歷史（包含來源）

```sql
SELECT
    m.id,
    m.role,
    m.content,
    m.sources,
    m.created_at
FROM messages m
WHERE m.conversation_id = 1
ORDER BY m.created_at ASC;
```

**結果**：
```json
[
  {
    "id": 1,
    "role": "user",
    "content": "Q3營收是多少？",
    "sources": null,
    "created_at": "2024-03-20 10:00:00"
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "根據文件，Q3營收為...",
    "sources": "[{\"doc_id\": 3, \"page\": 5}]",
    "created_at": "2024-03-20 10:00:03"
  }
]
```

### 查詢 4: 檢查使用者權限

```python
# Python 程式碼範例
def can_user_access_document(user_id: int, doc_id: int) -> bool:
    """檢查使用者是否有權訪問文件"""

    query = """
    SELECT
        gm.role AS user_role,
        d.min_view_role AS doc_role
    FROM documents d
    INNER JOIN group_members gm ON d.group_id = gm.group_id
    WHERE d.id = :doc_id
      AND gm.user_id = :user_id
      AND gm.is_active = TRUE
    """

    result = db.execute(query, {"doc_id": doc_id, "user_id": user_id}).first()

    if not result:
        return False  # 不是群組成員

    # 權限層級對照
    role_level = {
        'viewer': 0,
        'editor': 1,
        'admin': 2,
        'owner': 3
    }

    user_level = role_level[result.user_role]
    required_level = role_level[result.doc_role]

    return user_level >= required_level
```

---

## 資料完整性保證

### 1. 外鍵約束（Foreign Key）

**目的**：確保資料一致性

```sql
-- 範例：文件必須屬於存在的群組
FOREIGN KEY (group_id) REFERENCES groups(id)

-- 如果嘗試插入不存在的 group_id
INSERT INTO documents (group_id, ...) VALUES (999, ...);
-- 錯誤: Cannot add or update a child row: a foreign key constraint fails
```

### 2. 級聯刪除（CASCADE）

**目的**：刪除父資料時，自動刪除子資料

```sql
FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE

-- 範例：刪除群組時，自動刪除該群組的所有文件
DELETE FROM groups WHERE id = 2;
-- 自動執行:
-- DELETE FROM documents WHERE group_id = 2;
-- DELETE FROM group_members WHERE group_id = 2;
-- DELETE FROM conversations WHERE group_id = 2;
```

### 3. 設為 NULL（SET NULL）

**目的**：刪除父資料時，將子資料的外鍵設為 NULL

```sql
FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL

-- 範例：Alice 刪除帳號，但她邀請的成員記錄保留
DELETE FROM users WHERE id = 1;
-- Bob 的記錄變成:
-- invited_by: NULL (而不是刪除整筆記錄)
```

### 4. 唯一約束（UNIQUE）

**目的**：確保資料不重複

```sql
-- 使用者名稱不能重複
UNIQUE (username)

-- 同一使用者在同一群組只能有一個角色
UNIQUE KEY unique_group_user (group_id, user_id)
```

---

## 索引優化

### 什麼是索引？

想像查字典：

**沒有索引**：從第一頁翻到最後一頁找「蘋果」
**有索引**：看注音索引「ㄆ」，直接翻到該頁

### 我們的索引設計

```sql
-- 主鍵索引（自動建立）
PRIMARY KEY (id)

-- 唯一索引
UNIQUE (username)
UNIQUE (email)

-- 一般索引（加速查詢）
INDEX idx_group (group_id)      -- 常用於 WHERE group_id = ?
INDEX idx_user (user_id)        -- 常用於 WHERE user_id = ?
INDEX idx_status (processing_status)  -- 常用於篩選狀態
INDEX idx_created (created_at)  -- 常用於排序
```

### 複合索引

```sql
-- 針對常見查詢：「某群組的某使用者」
INDEX idx_group_user (group_id, user_id)

-- 好處：加速這類查詢
SELECT * FROM group_members WHERE group_id = 2 AND user_id = 1;
```

---

## 資料庫操作實戰

### 連線到 MySQL

```bash
# 進入 MySQL 容器
docker-compose exec mysql bash

# 登入 MySQL
mysql -u library_user -p
# 輸入密碼: library_pass

# 選擇資料庫
USE library_agent;
```

### 常用查詢

```sql
-- 查看所有資料表
SHOW TABLES;

-- 查看資料表結構
DESCRIBE users;

-- 查看所有使用者
SELECT * FROM users;

-- 查看某使用者的群組
SELECT g.name, gm.role
FROM groups g
INNER JOIN group_members gm ON g.id = gm.group_id
WHERE gm.user_id = 1;

-- 查看群組的文件數量
SELECT
    g.name,
    COUNT(d.id) AS doc_count
FROM groups g
LEFT JOIN documents d ON g.id = d.group_id
GROUP BY g.id, g.name;

-- 查看處理失敗的文件
SELECT original_filename, error_message
FROM documents
WHERE processing_status = 'failed';
```

### 資料備份

```bash
# 備份整個資料庫
docker-compose exec mysql mysqldump -u root -p library_agent > backup.sql

# 備份特定資料表
docker-compose exec mysql mysqldump -u root -p library_agent users groups > backup_users_groups.sql

# 還原資料庫
docker-compose exec -T mysql mysql -u root -p library_agent < backup.sql
```

---

## 效能考量

### 1. 避免 N+1 查詢問題

**壞範例**：
```python
# 查詢所有群組
groups = db.query(Group).all()

# 對每個群組查詢成員（N 次查詢）
for group in groups:
    members = db.query(GroupMember).filter_by(group_id=group.id).all()
```

**好範例**：
```python
# 一次查詢，使用 JOIN
result = db.query(Group, GroupMember)\
    .join(GroupMember, Group.id == GroupMember.group_id)\
    .all()
```

### 2. 使用分頁

```python
# 不要一次載入所有資料
# BAD
all_messages = db.query(Message).all()  # 可能有幾千筆

# GOOD
messages = db.query(Message)\
    .order_by(Message.created_at.desc())\
    .limit(20)\
    .offset(0)\
    .all()  # 只載入 20 筆
```

### 3. 善用快取

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_permissions(user_id: int, group_id: int):
    """快取使用者權限查詢"""
    # 這個查詢結果會被快取
    return db.query(...).first()
```

---

## 常見問題

### Q1: 為什麼不把文件內容存在資料庫？

**A**:
- 檔案太大（幾 MB 到幾十 MB）
- MySQL 的 BLOB 欄位效能差
- 備份和還原麻煩
- 改用檔案系統 + 資料庫元資料的混合方式

### Q2: JSON 欄位（sources）會不會影響效能？

**A**:
- MySQL 8.0 的 JSON 支援很好
- 我們只用來儲存，不用來查詢
- 如果要查詢，會放在獨立的資料表

### Q3: 為什麼要 member_count 和 document_count？

**A**:
- 避免每次都 COUNT(*)（效能差）
- 即時顯示數量
- 用觸發器或應用程式邏輯維護一致性

### Q4: 如何處理大量資料？

**A**:
- 目前設計：< 10,000 文件，< 1,000 使用者
- 擴展方案：
  - 分表（Sharding）
  - 讀寫分離
  - 遷移到 PostgreSQL（更好的並發）

---

## 下一步

現在你已經理解資料庫設計，接下來：

1. **學習 RAG 原理**：[04. RAG 基礎原理](04-rag-fundamentals.md)
2. **實作權限系統**：[07. 認證與權限系統](07-auth-permission.md)
3. **開始寫程式**：[08. 後端實作指南](08-backend-implementation.md)

---

## 延伸閱讀

- [MySQL 官方文件](https://dev.mysql.com/doc/)
- [SQLAlchemy ORM 教學](https://docs.sqlalchemy.org/en/20/orm/)
- [資料庫正規化](https://zh.wikipedia.org/wiki/数据库规范化)
