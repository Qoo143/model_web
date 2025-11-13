"""群組和群組成員模型"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class GroupRole(str, enum.Enum):
    """群組角色"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Group(Base):
    """群組模型"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_private = Column(Boolean, default=True)
    member_count = Column(Integer, default=1)
    document_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ============================================
    # 關聯關係
    # ============================================
    # 群組擁有者
    owner = relationship(
        "User",
        back_populates="owned_groups",
        foreign_keys=[owner_id]
    )

    # 群組成員
    members = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan"
    )

    # 群組文件
    documents = relationship(
        "Document",
        back_populates="group",
        cascade="all, delete-orphan"
    )

    # 群組對話
    conversations = relationship(
        "Conversation",
        back_populates="group",
        cascade="all, delete-orphan"
    )

class GroupMember(Base):
    """群組成員模型"""
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(Enum(GroupRole), default=GroupRole.VIEWER)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # ============================================
    # 關聯關係
    # ============================================
    # 所屬群組
    group = relationship(
        "Group",
        back_populates="members"
    )

    # 所屬使用者
    user = relationship(
        "User",
        back_populates="group_memberships"
    )
