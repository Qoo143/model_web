-- Library RAG Agent System - 資料庫初始化腳本
-- 此腳本會在 MySQL 容器首次啟動時自動執行

-- 設定字符集為 UTF-8 (支援中文)
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 使用資料庫
USE library_agent;

-- ============================================
-- 1. 使用者表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '使用者 ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '使用者名稱 (唯一)',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '電子郵件 (唯一)',
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密後的密碼',
    role ENUM('user', 'admin') DEFAULT 'user' COMMENT '角色: user=一般使用者, admin=管理員',
    department VARCHAR(50) COMMENT '部門 (用於權限控制)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '帳號是否啟用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',

    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='使用者資料表';

-- ============================================
-- 2. 群組表 (groups)
-- ============================================
CREATE TABLE IF NOT EXISTS groups (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '群組 ID',
    name VARCHAR(100) NOT NULL COMMENT '群組名稱',
    description TEXT COMMENT '群組描述',
    owner_id INT NOT NULL COMMENT '擁有者 ID (創建者)',
    is_private BOOLEAN DEFAULT TRUE COMMENT '是否為私有群組',
    allow_join_request BOOLEAN DEFAULT FALSE COMMENT '是否允許其他人申請加入',
    member_count INT DEFAULT 1 COMMENT '成員數量',
    document_count INT DEFAULT 0 COMMENT '文件數量',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組資料表';

-- ============================================
-- 3. 群組成員表 (group_members)
-- ============================================
CREATE TABLE IF NOT EXISTS group_members (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '成員關聯 ID',
    group_id INT NOT NULL COMMENT '群組 ID',
    user_id INT NOT NULL COMMENT '使用者 ID',
    role ENUM('owner', 'admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer' COMMENT '角色: owner > admin > editor > viewer',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入時間',
    invited_by INT COMMENT '邀請者 ID',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否為活躍成員',

    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL,

    UNIQUE KEY unique_group_user (group_id, user_id) COMMENT '確保同一使用者在同一群組中只有一個角色',
    INDEX idx_group (group_id),
    INDEX idx_user (user_id),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群組成員關聯表';

-- ============================================
-- 4. 文件表 (documents)
-- ============================================
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '文件 ID',
    filename VARCHAR(255) NOT NULL COMMENT '儲存的檔案名稱 (UUID)',
    original_filename VARCHAR(255) NOT NULL COMMENT '原始上傳的檔案名稱',
    file_type VARCHAR(20) NOT NULL COMMENT '檔案類型: pdf/docx/xlsx/txt/md',
    file_size BIGINT NOT NULL COMMENT '檔案大小 (bytes)',
    file_path VARCHAR(500) NOT NULL COMMENT '檔案儲存路徑',

    group_id INT NOT NULL COMMENT '所屬群組 ID',
    uploaded_by INT NOT NULL COMMENT '上傳者 ID',

    -- 權限設定
    min_view_role ENUM('owner', 'admin', 'editor', 'viewer') DEFAULT 'viewer' COMMENT '最低可查看角色',

    -- 處理狀態
    processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT '處理狀態',
    error_message TEXT COMMENT '錯誤訊息 (如果處理失敗)',

    -- 統計資訊
    chunk_count INT DEFAULT 0 COMMENT '文件切塊數量',
    page_count INT DEFAULT 0 COMMENT '頁數 (如果適用)',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上傳時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間',

    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE,

    INDEX idx_group (group_id),
    INDEX idx_uploader (uploaded_by),
    INDEX idx_status (processing_status),
    INDEX idx_filename (filename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件資料表';

-- ============================================
-- 5. 對話表 (conversations)
-- ============================================
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '對話 ID',
    user_id INT NOT NULL COMMENT '使用者 ID',
    group_id INT NOT NULL COMMENT '所屬群組 ID',
    title VARCHAR(200) COMMENT '對話標題 (自動生成或手動設定)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最後更新時間',

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,

    INDEX idx_user (user_id),
    INDEX idx_group (group_id),
    INDEX idx_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='對話資料表';

-- ============================================
-- 6. 訊息表 (messages)
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '訊息 ID',
    conversation_id INT NOT NULL COMMENT '所屬對話 ID',
    role ENUM('user', 'assistant') NOT NULL COMMENT '角色: user=使用者, assistant=AI',
    content TEXT NOT NULL COMMENT '訊息內容',

    -- 來源引用 (JSON 格式)
    sources JSON COMMENT '來源引用 JSON: [{"doc_id": 1, "page": 5, "chunk_index": 2, "content": "..."}]',

    -- 元資料
    token_count INT COMMENT 'Token 數量',
    generation_time FLOAT COMMENT '生成時間 (秒)',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間',

    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,

    INDEX idx_conversation (conversation_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='訊息資料表';

-- ============================================
-- 初始資料 (可選)
-- ============================================

-- 創建一個測試使用者 (密碼: test123)
-- 注意: 這是 bcrypt 加密後的 'test123'
INSERT INTO users (username, email, hashed_password, role) VALUES
('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NAuJC6eJWJfC', 'user')
ON DUPLICATE KEY UPDATE username=username;

-- 為測試使用者創建一個個人群組
INSERT INTO groups (name, description, owner_id, is_private) VALUES
('我的文件庫', '個人文件管理空間', 1, TRUE)
ON DUPLICATE KEY UPDATE name=name;

-- 將使用者加入群組 (作為 owner)
INSERT INTO group_members (group_id, user_id, role) VALUES
(1, 1, 'owner')
ON DUPLICATE KEY UPDATE role=role;

-- ============================================
-- 完成
-- ============================================
SELECT 'Database initialization completed!' AS status;
