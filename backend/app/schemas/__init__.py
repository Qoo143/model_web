"""
Schemas 套件

匯出所有 Pydantic schemas，方便 API 使用
"""

from app.schemas.user import (
    UserBase,
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    TokenResponse,
    MessageResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserDetailResponse",
    "TokenResponse",

    # Common schemas
    "MessageResponse",
]
