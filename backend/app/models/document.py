"""文件模型"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DocumentStatus(str, enum.Enum):
    """文件處理狀態"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentRole(str, enum.Enum):
    """文件最低查看權限"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Document(Base):
    """文件模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_path = Column(String(500), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    processing_status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    min_view_role = Column(Enum(DocumentRole), default=DocumentRole.VIEWER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ============================================
    # 關聯關係
    # ============================================
    # 所屬群組
    group = relationship(
        "Group",
        back_populates="documents"
    )

    # 上傳者
    uploader = relationship(
        "User",
        back_populates="uploaded_documents",
        foreign_keys=[uploader_id]
    )
