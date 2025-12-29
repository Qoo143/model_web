---
name: backend-skills
description: >
  後端開發技能集合。包含 API、Database、Auth 等主題。
  當用戶詢問 FastAPI、SQLAlchemy、認證相關問題時觸發。
tags: [backend, fastapi, python]
---

# Backend Skills

後端使用 **FastAPI** + **SQLAlchemy 2.0** + **LangChain** 架構。

## 子主題

| Skill | 說明 | 觸發關鍵字 |
|:------|:-----|:-----------|
| [api](./api/SKILL.md) | API 路由開發 | api, endpoint, route |
| [database](./database/SKILL.md) | 資料庫操作 | database, model, migration |
| [auth](./auth/SKILL.md) | 認證授權 | auth, JWT, permission |

## 目錄結構

```
backend/app/
├── api/               # API 路由
├── models/            # SQLAlchemy 模型
├── schemas/           # Pydantic 驗證
├── services/          # 業務邏輯
│   ├── llm/          # LLM 服務
│   ├── rag/          # RAG 核心
│   ├── document/     # 文件處理
│   └── auth/         # 認證服務
├── core/              # 核心配置
└── utils/             # 工具函數
```
