---
name: backend-database
description: >
  資料庫操作規範。當用戶詢問 "database"、"model"、
  "SQLAlchemy"、"migration"、"Alembic" 時觸發此 Skill。
tags: [backend, database, sqlalchemy]
---

# 資料庫操作規範

## 模型定義

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # 關聯
    group = relationship("Group", back_populates="documents")
```

## 核心資料表

| 表名 | 說明 | 主要欄位 |
|:-----|:-----|:---------|
| `users` | 使用者 | id, username, email, role |
| `groups` | 群組 | id, name, owner_id |
| `group_members` | 成員關係 | group_id, user_id, role |
| `documents` | 文件 | id, group_id, filename, status |
| `conversations` | 對話 | id, user_id, group_id |
| `messages` | 訊息 | id, conversation_id, role, content |

## Alembic 遷移

```bash
# 生成遷移
alembic revision --autogenerate -m "Add new column"

# 執行遷移
alembic upgrade head

# 回滾
alembic downgrade -1
```

## 詳細參考

→ [reference/database-schema.md](./reference/database-schema.md) - 完整資料庫結構
