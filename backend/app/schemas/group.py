"""
群組 Schema

定義群組和群組成員的 API 請求和回應格式
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.group import GroupRole


# ============================================
# 群組基礎 Schema
# ============================================
class GroupBase(BaseModel):
    """群組基礎 Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="群組名稱")
    description: Optional[str] = Field(None, max_length=1000, description="群組描述")
    is_private: bool = Field(default=True, description="是否為私有群組")


# ============================================
# 群組請求 Schema
# ============================================
class GroupCreate(GroupBase):
    """
    建立群組 Schema

    業務邏輯：
    - 建立者自動成為群組擁有者
    - 預設為私有群組
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "技術文件庫",
                "description": "存放技術相關文件",
                "is_private": True
            }
        }
    )


class GroupUpdate(BaseModel):
    """
    更新群組 Schema

    業務邏輯：
    - 所有欄位都是可選的
    - 只更新提供的欄位
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    is_private: Optional[bool] = None


# ============================================
# 群組成員 Schema
# ============================================
class GroupMemberAdd(BaseModel):
    """
    新增群組成員 Schema

    業務邏輯：
    - 只有 owner 和 admin 可以邀請成員
    - 預設角色為 viewer
    """
    user_id: int = Field(..., description="要新增的使用者 ID")
    role: GroupRole = Field(default=GroupRole.VIEWER, description="成員角色")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 2,
                "role": "editor"
            }
        }
    )


class GroupMemberUpdate(BaseModel):
    """
    更新群組成員角色 Schema

    業務邏輯：
    - 只有 owner 可以更新 admin 的角色
    - admin 可以更新 editor 和 viewer 的角色
    """
    role: GroupRole = Field(..., description="新的角色")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "editor"
            }
        }
    )


class GroupMemberResponse(BaseModel):
    """群組成員回應 Schema"""
    id: int
    user_id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: GroupRole
    joined_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================
# 群組回應 Schema
# ============================================
class GroupResponse(GroupBase):
    """群組基本回應 Schema"""
    id: int
    owner_id: int
    member_count: int
    document_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GroupDetailResponse(GroupResponse):
    """
    群組詳細回應 Schema

    包含成員列表和當前使用者的角色
    """
    owner_username: str
    current_user_role: Optional[GroupRole] = None
    members: List[GroupMemberResponse] = []

    model_config = ConfigDict(from_attributes=True)


class GroupListResponse(BaseModel):
    """群組列表回應 Schema"""
    total: int
    groups: List[GroupResponse]


# ============================================
# 通用訊息回應
# ============================================
class MessageResponse(BaseModel):
    """通用訊息回應"""
    message: str = Field(..., description="訊息內容")
    detail: Optional[str] = Field(None, description="詳細資訊")
