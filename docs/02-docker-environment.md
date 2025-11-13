# 02. Docker 環境設置 - 從零開始

## Docker 是什麼？（用比喻理解）

### 傳統開發方式的問題

想像你要邀請朋友來家裡玩遊戲：

```
你的電腦：Windows 11, Python 3.11, MySQL 8.0
朋友的電腦：macOS, Python 3.9, MySQL 5.7

結果：
❌ 朋友： "欸，為什麼我這邊跑不起來？"
❌ 你："在我電腦上明明可以啊！"
```

### Docker 的解決方案

Docker 就像把你的應用裝在「貨櫃」裡：

```
┌────────────────────────────┐
│  Docker Container (貨櫃)    │
│  ┌──────────────────────┐  │
│  │  你的應用              │  │
│  │  + Python 3.11        │  │
│  │  + MySQL 8.0          │  │
│  │  + 所有依賴            │  │
│  └──────────────────────┘  │
└────────────────────────────┘

✅ 在任何電腦上都一樣運行
✅ Windows / macOS / Linux 通用
✅ 不會互相干擾
```

**關鍵優勢**：
- **環境一致**：開發環境 = 測試環境 = 生產環境
- **隔離性**：各個服務不會互相影響
- **易於分享**：別人可以一鍵啟動你的專案
- **易於清理**：不想要了就刪掉容器，不留垃圾

---

## Docker 核心概念

### 1. Image (映像檔) vs Container (容器)

**Image** = 食譜（藍圖）
**Container** = 實際做出來的菜（實例）

```
┌─────────────┐
│   Image     │  例如：Python 3.11 的映像檔
│  (食譜)      │  - 包含 Python 直譯器
└──────┬──────┘  - 包含基本函式庫
       │
       ├──► Container 1 (容器 A)
       ├──► Container 2 (容器 B)
       └──► Container 3 (容器 C)

一個 Image 可以產生多個 Container
```

### 2. Dockerfile

定義如何建立 Image 的腳本：

```dockerfile
# 從 Python 3.11 開始
FROM python:3.11

# 設定工作目錄
WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install -r requirements.txt

# 複製應用程式
COPY . .

# 啟動命令
CMD ["python", "app.py"]
```

**比喻**：就像食譜一樣，一步一步告訴 Docker 怎麼做。

### 3. docker-compose.yml

管理多個容器的編排檔：

```yaml
services:
  backend:   # 後端服務
  frontend:  # 前端服務
  mysql:     # 資料庫服務
  ollama:    # LLM 服務
```

**比喻**：就像餐廳的菜單，列出所有要提供的「服務」。

### 4. Volume (資料持久化)

Container 刪除後，資料也會消失。Volume 可以保存資料：

```
Container (容器)                  Volume (持久化儲存)
┌──────────────┐                 ┌──────────────┐
│              │   寫入資料        │              │
│   MySQL      ├────────────────►│  mysql_data  │
│              │                 │              │
└──────────────┘                 └──────────────┘

就算容器刪除，Volume 的資料還在
```

---

## 安裝 Docker

### Windows (推薦 Docker Desktop)

#### 步驟 1: 下載 Docker Desktop
1. 前往 https://www.docker.com/products/docker-desktop/
2. 下載 Windows 版本
3. 執行安裝檔

#### 步驟 2: 啟用 WSL 2 (Windows Subsystem for Linux)

打開 PowerShell（系統管理員）：

```powershell
# 啟用 WSL
wsl --install

# 重新啟動電腦
```

#### 步驟 3: 啟動 Docker Desktop

安裝完成後：
1. 開啟 Docker Desktop
2. 等待 Docker 引擎啟動（托盤圖示變綠色）

#### 步驟 4: 驗證安裝

打開 PowerShell 或 CMD：

```bash
# 檢查 Docker 版本
docker --version
# 輸出: Docker version 24.0.7, build...

# 檢查 Docker Compose 版本
docker-compose --version
# 輸出: Docker Compose version v2.23.0

# 測試運行
docker run hello-world
# 如果成功，會顯示歡迎訊息
```

### macOS (Docker Desktop)

#### 步驟 1: 下載並安裝
1. 前往 https://www.docker.com/products/docker-desktop/
2. 選擇 Mac 版本（Intel 或 Apple Silicon）
3. 拖曳到 Applications 資料夾

#### 步驟 2: 啟動和驗證

```bash
# 檢查版本
docker --version
docker-compose --version

# 測試
docker run hello-world
```

### Linux (Ubuntu/Debian)

#### 步驟 1: 安裝 Docker Engine

```bash
# 更新套件列表
sudo apt-get update

# 安裝必要套件
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 加入 Docker 官方 GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 加入 Docker 套件源
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安裝 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 安裝 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 步驟 2: 設定權限（避免每次都要 sudo）

```bash
# 將當前使用者加入 docker 群組
sudo usermod -aG docker $USER

# 重新登入或執行
newgrp docker

# 測試（不需要 sudo）
docker run hello-world
```

---

## AMD GPU 支援配置（選讀）

如果你有 AMD 顯卡，可以讓 Ollama 使用 GPU 加速。

### 檢查你的 AMD GPU

```bash
# Linux
lspci | grep VGA

# 輸出範例:
# 03:00.0 VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Navi 22 [Radeon RX 6700/6700 XT/6750 XT / 6800M/6850M XT]
```

### 安裝 ROCm（AMD 的 CUDA 等價物）

**支援的 GPU**：
- RX 6000 系列（Navi 21/22/23）
- RX 7000 系列（Navi 31/32/33）
- 部分 Vega 系列

#### Linux (Ubuntu 22.04)

```bash
# 加入 ROCm 套件源
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/jammy/amdgpu-install_5.7.50700-1_all.deb
sudo apt-get install ./amdgpu-install_5.7.50700-1_all.deb

# 安裝 ROCm
sudo amdgpu-install --usecase=rocm

# 將使用者加入 render 和 video 群組
sudo usermod -aG render $USER
sudo usermod -aG video $USER

# 重新登入
```

#### 驗證 ROCm

```bash
# 檢查 ROCm 版本
rocm-smi

# 輸出範例:
# ======================= ROCm System Management Interface =======================
# ================================== Concise Info =================================
# GPU  Temp   AvgPwr  SCLK    MCLK    Fan  Perf  PwrCap  VRAM%  GPU%
# 0    45.0c  15.0W   500Mhz  96Mhz   0%   auto  230.0W    1%   0%
```

### 配置 Docker 使用 AMD GPU

在 `docker-compose.yml` 中：

```yaml
ollama:
  devices:
    - /dev/kfd:/dev/kfd      # AMD GPU 核心
    - /dev/dri:/dev/dri      # AMD GPU DRM
  environment:
    - HSA_OVERRIDE_GFX_VERSION=10.3.0  # 根據你的 GPU 調整
```

**GFX 版本對照表**：
- RX 6700 XT: 10.3.0
- RX 6800/6900 XT: 10.3.0
- RX 7900 XT/XTX: 11.0.0

**如果沒有 AMD GPU**：
只要註解掉 `devices` 和 `HSA_OVERRIDE_GFX_VERSION`，Ollama 會自動使用 CPU。

---

## 啟動專案

### 步驟 1: 準備環境變數

```bash
# 進入專案目錄
cd c:\Users\wayne\OneDrive\Desktop\model_web

# 複製環境變數範例
cp .env.example .env

# (可選) 編輯 .env 修改密碼等設定
```

### 步驟 2: 啟動所有服務

```bash
# 啟動所有容器（第一次會下載映像檔,需要一些時間）
docker-compose up -d

# 參數說明:
# -d : detached mode (背景執行)
```

**第一次啟動會看到**：

```
[+] Running 5/5
 ⠿ Network library_network       Created
 ⠿ Volume "mysql_data"           Created
 ⠿ Container library_mysql       Started
 ⠿ Container library_ollama      Started
 ⠿ Container library_backend     Started
 ⠿ Container library_frontend    Started
```

**下載進度**：
```
[+] Building 123.4s (15/15) FINISHED
 => [mysql] pulling from library/mysql:8.0
 => [ollama] pulling from ollama/ollama:latest
 => [backend] building...
 => [frontend] building...
```

### 步驟 3: 檢查容器狀態

```bash
# 查看所有容器
docker-compose ps

# 輸出範例:
# NAME                 IMAGE              STATUS         PORTS
# library_mysql        mysql:8.0          Up 2 minutes   0.0.0.0:3306->3306/tcp
# library_ollama       ollama/ollama      Up 2 minutes   0.0.0.0:11434->11434/tcp
# library_backend      backend_image      Up 1 minute    0.0.0.0:8000->8000/tcp
# library_frontend     frontend_image     Up 1 minute    0.0.0.0:5173->5173/tcp
```

**狀態說明**：
- `Up X minutes`: 正常運行
- `Restarting`: 不斷重啟（有問題）
- `Exited (1)`: 已停止（有錯誤）

### 步驟 4: 查看日誌

```bash
# 查看所有服務的日誌
docker-compose logs

# 查看特定服務的日誌
docker-compose logs backend

# 即時追蹤日誌（類似 tail -f）
docker-compose logs -f backend

# 只看最後 100 行
docker-compose logs --tail=100 backend
```

### 步驟 5: 驗證服務

打開瀏覽器測試：

1. **前端**：http://localhost:5173
   - 應該看到登入頁面

2. **後端 API 文件**：http://localhost:8000/docs
   - FastAPI 自動生成的文件

3. **後端健康檢查**：http://localhost:8000/health
   - 應該返回 `{"status": "ok"}`

4. **Ollama**：http://localhost:11434
   - 應該返回 `Ollama is running`

---

## Docker 常用指令

### 容器管理

```bash
# 啟動所有服務
docker-compose up -d

# 停止所有服務（容器保留）
docker-compose stop

# 停止並移除容器
docker-compose down

# 重新啟動特定服務
docker-compose restart backend

# 重新建立並啟動（當 Dockerfile 有改動時）
docker-compose up -d --build
```

### 查看狀態

```bash
# 查看所有容器
docker-compose ps

# 查看容器資源使用（CPU、記憶體）
docker stats

# 查看特定容器的詳細資訊
docker inspect library_backend
```

### 進入容器

```bash
# 進入容器的 shell
docker-compose exec backend bash

# 在容器內執行命令（不進入 shell）
docker-compose exec backend ls /app

# 執行 Python shell
docker-compose exec backend python
```

### 查看日誌

```bash
# 所有服務
docker-compose logs

# 特定服務
docker-compose logs mysql

# 即時追蹤
docker-compose logs -f

# 最後 N 行
docker-compose logs --tail=50 backend
```

### 資料管理

```bash
# 列出所有 Volume
docker volume ls

# 查看 Volume 詳細資訊
docker volume inspect mysql_data

# 備份 Volume (重要！)
docker run --rm \
  -v mysql_data:/source \
  -v $(pwd)/backup:/backup \
  alpine \
  tar czf /backup/mysql-backup-$(date +%Y%m%d).tar.gz -C /source .

# 刪除未使用的 Volume
docker volume prune
```

### 清理

```bash
# 停止並移除容器
docker-compose down

# 停止、移除容器，並刪除 Volume（危險！資料會遺失）
docker-compose down -v

# 清理未使用的映像檔
docker image prune

# 清理所有未使用的資源
docker system prune -a
```

---

## 資料持久化說明

我們的專案使用兩種持久化方式：

### 方式 1: Docker Volume (MySQL)

**優點**：
- Docker 自動管理
- 跨平台相容性好
- 效能較好

**缺點**：
- 不容易直接存取
- 需要用指令備份

**使用場景**：資料庫檔案（MySQL）

```yaml
services:
  mysql:
    volumes:
      - mysql_data:/var/lib/mysql  # Volume 掛載

volumes:
  mysql_data:  # 定義 Volume
```

**資料位置**：
- Windows: `\\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\`
- Linux: `/var/lib/docker/volumes/`
- macOS: `~/Library/Containers/com.docker.docker/Data/vms/0/`

### 方式 2: 目錄掛載 (Bind Mount)

**優點**：
- 可直接存取宿主機檔案
- 容易備份
- 方便開發（修改檔案立即生效）

**缺點**：
- 路徑必須存在
- 權限問題（Linux）

**使用場景**：
- 文件儲存 (`storage/documents/`)
- Chroma 資料庫 (`storage/chroma_db/`)
- Ollama 模型 (`storage/ollama/`)
- 開發時的程式碼

```yaml
services:
  backend:
    volumes:
      - ./backend:/app                          # 程式碼
      - ./storage/documents:/app/storage/documents  # 文件
      - ./storage/chroma_db:/app/storage/chroma_db  # Chroma
```

**資料位置**：就在專案目錄下的 `storage/`

---

## 初次啟動後的設定

### 1. 下載 Ollama 模型

Ollama 容器啟動後，需要手動下載模型：

```bash
# 進入 Ollama 容器
docker-compose exec ollama bash

# 下載 gpt-oss-20b 模型（約 10-20GB，需要時間）
ollama pull gpt-oss-20b

# 驗證模型
ollama list
# 輸出:
# NAME             ID              SIZE      MODIFIED
# gpt-oss-20b      abc123...       12 GB     2 minutes ago

# 測試模型
ollama run gpt-oss-20b "你好"
# 應該會回覆中文

# 離開容器
exit
```

**下載時間估計**：
- 100Mbps 網路: ~20 分鐘
- 50Mbps 網路: ~40 分鐘
- 10Mbps 網路: ~3 小時

### 2. 驗證資料庫初始化

```bash
# 進入 MySQL 容器
docker-compose exec mysql bash

# 登入 MySQL
mysql -u library_user -p
# 輸入密碼: library_pass (或你在 .env 設定的)

# 選擇資料庫
USE library_agent;

# 查看資料表
SHOW TABLES;
# 輸出:
# +-------------------------+
# | Tables_in_library_agent |
# +-------------------------+
# | conversations           |
# | documents               |
# | group_members           |
# | groups                  |
# | messages                |
# | users                   |
# +-------------------------+

# 查看測試使用者
SELECT * FROM users;
# 應該有一個 testuser

# 離開
exit
exit
```

### 3. 測試後端 API

```bash
# 測試健康檢查
curl http://localhost:8000/health

# 測試登入（使用測試帳號）
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'

# 應該返回 JWT Token
```

---

## 常見問題除錯

### 問題 1: 容器不斷重啟

**症狀**：
```bash
docker-compose ps
# STATUS: Restarting (1) 10 seconds ago
```

**解決方法**：

1. 查看日誌找出錯誤
```bash
docker-compose logs backend
```

2. 常見原因：
   - 資料庫連線失敗 → 檢查 `.env` 的資料庫密碼
   - 程式碼語法錯誤 → 查看錯誤訊息
   - 缺少依賴 → 重新建立映像檔 `docker-compose build`

### 問題 2: 無法連線到服務

**症狀**：瀏覽器顯示「無法連線」

**解決方法**：

1. 檢查容器是否運行
```bash
docker-compose ps
```

2. 檢查 port 是否被佔用
```bash
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000
```

3. 如果 port 被佔用，修改 `docker-compose.yml`：
```yaml
backend:
  ports:
    - "8001:8000"  # 改用 8001
```

### 問題 3: MySQL 無法啟動

**症狀**：
```bash
docker-compose logs mysql
# Error: Cannot start MySQL server
```

**解決方法**：

1. 刪除 Volume 重新初始化（注意：資料會遺失！）
```bash
docker-compose down -v
docker-compose up -d
```

2. 檢查密碼設定是否正確
```bash
cat .env | grep MYSQL
```

### 問題 4: AMD GPU 無法使用

**症狀**：
```bash
docker-compose logs ollama
# Error: No GPU detected
```

**解決方法**：

1. 檢查 ROCm 是否安裝
```bash
rocm-smi
```

2. 檢查裝置是否掛載
```bash
ls -l /dev/kfd /dev/dri
```

3. 如果還是不行，先用 CPU 運行
```yaml
# 註解掉 GPU 相關設定
# devices:
#   - /dev/kfd:/dev/kfd
#   - /dev/dri:/dev/dri
```

### 問題 5: 磁碟空間不足

**症狀**：
```bash
Error: no space left on device
```

**解決方法**：

1. 查看 Docker 使用的空間
```bash
docker system df
```

2. 清理未使用的資源
```bash
# 清理映像檔
docker image prune -a

# 清理容器
docker container prune

# 清理 Volume
docker volume prune

# 清理所有
docker system prune -a
```

---

## 開發工作流程

### 修改程式碼後

**前端**：
```bash
# 不需要重啟！Vite 會自動熱更新
# 只要儲存檔案，瀏覽器會自動重新載入
```

**後端**：
```bash
# FastAPI 的 --reload 模式會自動重新載入
# 但如果修改 requirements.txt，需要重新建立
docker-compose up -d --build backend
```

### 修改 Docker 配置後

```bash
# 修改 docker-compose.yml 或 Dockerfile
docker-compose down
docker-compose up -d --build
```

### 資料庫遷移

```bash
# 修改資料表結構後（未來會用 Alembic）
docker-compose exec backend alembic upgrade head
```

---

## 生產環境部署注意事項

### 1. 修改預設密碼

```bash
# .env
MYSQL_ROOT_PASSWORD=超強密碼123!@#
SECRET_KEY=一個很長很隨機的字串
```

### 2. 移除測試資料

編輯 `docker/mysql/init.sql`，刪除：
```sql
-- 這些是測試用的，生產環境要移除
INSERT INTO users ...
INSERT INTO groups ...
```

### 3. 關閉開發模式

```yaml
# docker-compose.yml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000
  # 移除 --reload
```

### 4. 使用環境變數管理敏感資訊

不要把 `.env` 提交到 Git！

```bash
# .gitignore
.env
```

### 5. 設定備份策略

```bash
# 每日備份 MySQL
0 2 * * * docker-compose exec mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD library_agent > backup/db-$(date +\%Y\%m\%d).sql

# 每日備份 Chroma
0 3 * * * tar czf backup/chroma-$(date +\%Y\%m\%d).tar.gz storage/chroma_db/
```

---

## 下一步

現在你已經成功啟動 Docker 環境了！接下來：

1. **理解資料庫設計**：[03. 資料庫設計](03-database-design.md)
2. **學習 RAG 原理**：[04. RAG 基礎原理](04-rag-fundamentals.md)
3. **配置 Ollama**：[06. Ollama 與 LLM 整合](06-ollama-llm.md)

---

## 學習資源

- [Docker 官方教學](https://docs.docker.com/get-started/)
- [Docker Compose 文件](https://docs.docker.com/compose/)
- [ROCm 官方文件](https://rocm.docs.amd.com/)
