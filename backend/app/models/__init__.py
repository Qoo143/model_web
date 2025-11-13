"""
資料庫模型

匯出所有模型，方便其他模組使用
特別重要：Alembic 會從這裡自動檢測所有模型
"""

from app.models.user import User, UserRole
from app.models.group import Group, GroupMember, GroupRole
from app.models.document import Document, DocumentStatus, DocumentRole
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole

__all__ = [
    # User models
    "User",
    "UserRole",

    # Group models
    "Group",
    "GroupMember",
    "GroupRole",

    # Document models
    "Document",
    "DocumentStatus",
    "DocumentRole",

    # Conversation models
    "Conversation",
    "Message",
    "MessageRole",
]
