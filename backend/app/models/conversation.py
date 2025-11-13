"""
對話模型

業務邏輯：
- 每個對話屬於一個使用者和一個群組
- 群組決定了問答的文件範圍
- 對話標題可以自動生成（基於第一個問題）
- 追蹤對話中的訊息數量
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Conversation(Base):
    """
    對話表

    關聯關係：
    - 屬於一個使用者 (user_id)
    - 屬於一個群組 (group_id) - 決定問答範圍
    - 包含多個訊息 (messages)
    """
    __tablename__ = "conversations"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="對話 ID")

    # 外鍵
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="使用者 ID"
    )
    group_id = Column(
        Integer,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="群組 ID（問答範圍）"
    )

    # 對話資訊
    title = Column(
        String(200),
        nullable=True,
        comment="對話標題（自動生成或使用者設定）"
    )

    # 統計資訊
    message_count = Column(
        Integer,
        default=0,
        comment="訊息數量"
    )

    # 時間戳記
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
        comment="最後更新時間"
    )

    # ============================================
    # 關聯關係
    # ============================================
    # 屬於哪個使用者
    user = relationship(
        "User",
        back_populates="conversations"
    )

    # 屬於哪個群組
    group = relationship(
        "Group",
        back_populates="conversations"
    )

    # 包含的訊息
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",  # 刪除對話時同時刪除所有訊息
        order_by="Message.created_at"  # 按時間排序
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title='{self.title}')>"