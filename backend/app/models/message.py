"""
訊息模型

業務邏輯：
- 訊息分為使用者訊息和助手回覆
- 助手訊息包含來源引用（JSON 格式）
- 記錄 Token 數量和生成時間用於統計
- 記錄使用的模型名稱
"""

import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MessageRole(str, enum.Enum):
    """
    訊息角色枚舉

    USER: 使用者提問
    ASSISTANT: AI 助手回答
    """
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    """
    訊息表

    關聯關係：
    - 屬於一個對話 (conversation_id)
    - 區分使用者訊息和助手訊息

    JSON 欄位說明：
    sources: 來源引用列表
    [
        {
            "doc_id": 1,
            "doc_name": "report.pdf",
            "page": 5,
            "chunk_index": 2,
            "content": "相關內容片段...",
            "score": 0.89  # 相似度分數
        },
        ...
    ]
    """
    __tablename__ = "messages"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="訊息 ID")

    # 外鍵
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="對話 ID"
    )

    # 訊息內容
    role = Column(
        Enum(MessageRole),
        nullable=False,
        index=True,
        comment="角色：user/assistant"
    )
    content = Column(
        Text,
        nullable=False,
        comment="訊息內容"
    )

    # 來源引用（僅 assistant 訊息有）
    sources = Column(
        JSON,
        nullable=True,
        comment="來源引用（JSON 格式）"
    )

    # 元資料（用於統計和監控）
    token_count = Column(
        Integer,
        nullable=True,
        comment="Token 數量"
    )
    generation_time = Column(
        Float,
        nullable=True,
        comment="生成時間（秒）"
    )
    model_used = Column(
        String(50),
        nullable=True,
        comment="使用的模型名稱"
    )

    # 時間戳記
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        comment="建立時間"
    )

    # ============================================
    # 關聯關係
    # ============================================
    # 屬於哪個對話
    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    def __repr__(self):
        preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message(id={self.id}, role={self.role}, content='{preview}')>"

    @property
    def has_sources(self) -> bool:
        """是否包含來源引用"""
        return self.sources is not None and len(self.sources) > 0

    @property
    def source_count(self) -> int:
        """來源引用數量"""
        return len(self.sources) if self.sources else 0
