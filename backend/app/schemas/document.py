"""
文件 Schema

定義文件上傳和管理的 API 請求和回應格式
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.document import DocumentStatus, DocumentRole


# ============================================
# 文件基礎 Schema
# ============================================
class DocumentBase(BaseModel):
    """文件基礎 Schema"""
    min_view_role: DocumentRole = Field(
        default=DocumentRole.VIEWER,
        description="查看此文件所需的最低權限"
    )


# ============================================
# 文件請求 Schema
# ============================================
class DocumentCreate(DocumentBase):
    """
    上傳文件 Schema

    業務邏輯：
    - 文件只能透過 multipart/form-data 上傳
    - 這個 Schema 用於驗證額外的表單欄位
    """
    group_id: int = Field(..., description="文件所屬群組 ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "group_id": 1,
                "min_view_role": "viewer"
            }
        }
    )


class DocumentUpdate(BaseModel):
    """
    更新文件 Schema

    業務邏輯：
    - 目前只能更新查看權限
    """
    min_view_role: Optional[DocumentRole] = None


# ============================================
# 文件回應 Schema
# ============================================
class DocumentResponse(BaseModel):
    """文件基本回應 Schema"""
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    group_id: int
    uploader_id: int
    uploader_username: Optional[str] = None
    processing_status: DocumentStatus
    error_message: Optional[str] = None
    chunk_count: int
    page_count: int
    min_view_role: DocumentRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(DocumentResponse):
    """
    文件詳細回應 Schema

    包含群組資訊
    """
    group_name: str

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """文件列表回應 Schema"""
    total: int
    documents: List[DocumentResponse]


# ============================================
# 文件處理狀態回應
# ============================================
class DocumentProcessingStatus(BaseModel):
    """文件處理狀態回應"""
    document_id: int
    status: DocumentStatus
    progress: Optional[int] = Field(None, ge=0, le=100, description="處理進度 0-100%")
    error_message: Optional[str] = None
    chunk_count: Optional[int] = None


# ============================================
# 通用回應
# ============================================
class MessageResponse(BaseModel):
    """通用訊息回應"""
    message: str = Field(..., description="訊息內容")
    detail: Optional[str] = Field(None, description="詳細資訊")


class UploadResponse(BaseModel):
    """上傳回應 Schema"""
    message: str
    document: DocumentResponse
