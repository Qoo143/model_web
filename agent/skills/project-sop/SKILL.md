---
name: project-sop
description: >
  專案標準作業程序。當用戶詢問 "docker"、"部署"、
  "setup"、"環境"、"啟動" 時觸發此 Skill。
tags: [sop, docker, deployment]
---

# 專案 SOP

## 環境需求

| 項目 | 需求 |
|:-----|:-----|
| Docker | 24.0+ |
| Docker Compose | 2.20+ |
| GPU | 可選 (Ollama 加速) |

## 快速啟動

```bash
# 1. 複製環境變數
cp .env.example .env

# 2. 啟動所有服務
docker-compose up -d

# 3. 檢查服務狀態
docker-compose ps
```

## 服務列表

| 服務 | 端口 | 說明 |
|:-----|:-----|:-----|
| frontend | 3000 | Vue 前端 |
| backend | 8000 | FastAPI 後端 |
| mysql | 3306 | 資料庫 |
| chroma | 8001 | 向量庫 |
| ollama | 11434 | LLM 服務 |

## 開發模式

```bash
# 前端開發（熱更新）
cd frontend
npm run dev

# 後端開發
cd backend
uvicorn app.main:app --reload
```

## 資料庫遷移

```bash
# 進入 backend 容器
docker-compose exec backend bash

# 執行遷移
alembic upgrade head
```

## 詳細參考

→ [reference/docker-setup.md](./reference/docker-setup.md) - 完整 Docker 設置指南
