"""
使用者 Schema

定義 API 請求和回應的資料格式
使用 Pydantic 進行資料驗證
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# ============================================
# 基礎 Schema
# ============================================
class UserBase(BaseModel):
    """使用者基礎 Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="使用者名稱")
    email: EmailStr = Field(..., description="電子郵件")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


# ============================================
# 請求 Schema (Request)
# ============================================
class UserRegister(UserBase):
    """
    使用者註冊 Schema

    業務邏輯：
    - 密碼最少 8 個字元
    - 使用者名稱 3-50 字元
    - Email 格式驗證
    """
    password: str = Field(..., min_length=8, max_length=100, description="密碼")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "securepassword123"
            }
        }
    )


class UserLogin(BaseModel):
    """
    使用者登入 Schema

    業務邏輯：
    - 可以使用 username 或 email 登入
    - 這裡簡化為只用 username
    """
    username: str = Field(..., description="使用者名稱或 Email")
    password: str = Field(..., description="密碼")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "testuser",
                "password": "securepassword123"
            }
        }
    )


class UserUpdate(BaseModel):
    """
    使用者更新 Schema

    業務邏輯：
    - 所有欄位都是可選的
    - 只更新提供的欄位
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# ============================================
# 回應 Schema (Response)
# ============================================
class UserResponse(UserBase):
    """
    使用者回應 Schema

    業務邏輯：
    - 不包含敏感資訊（密碼）
    - 用於 API 回應
    """
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """
    使用者詳細資訊回應 Schema

    業務邏輯：
    - 包含統計資訊
    - 用於個人資料頁面
    """
    owned_groups_count: Optional[int] = 0
    joined_groups_count: Optional[int] = 0
    documents_count: Optional[int] = 0
    conversations_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    Token 回應 Schema

    業務邏輯：
    - JWT Token 認證
    - 前端儲存 access_token 用於後續請求
    """
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    user: UserResponse = Field(..., description="使用者資訊")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "testuser",
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "role": "user",
                    "is_active": True,
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00"
                }
            }
        }
    )


# ============================================
# 通用回應 Schema
# ============================================
class MessageResponse(BaseModel):
    """通用訊息回應"""
    message: str = Field(..., description="訊息內容")
    detail: Optional[str] = Field(None, description="詳細資訊")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "操作成功",
                "detail": "使用者已成功註冊"
            }
        }
    )
