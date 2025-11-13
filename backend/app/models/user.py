"""
使用者模型

對應資料庫 users 表
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """
    系統角色列舉

    業務邏輯:
    - USER: 一般使用者（預設）
    - ADMIN: 系統管理員（可管理所有資源）
    """
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    使用者模型

    業務邏輯:
    - 儲存使用者基本資料
    - 密碼加密儲存（hashed_password）
    - is_active 控制帳號啟用狀態
    - role 決定系統權限

    欄位說明:
    - id: 主鍵（自動遞增）
    - username: 使用者名稱（唯一）
    - email: 電子郵件（唯一）
    - hashed_password: 加密後的密碼
    - role: 系統角色
    - is_active: 是否啟用
    - created_at: 建立時間（自動）
    - updated_at: 更新時間（自動）
    """
    __tablename__ = "users"

    # 主鍵
    id = Column(Integer, primary_key=True, index=True, comment="使用者 ID")

    # 基本資訊
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="使用者名稱（唯一）"
    )
    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="電子郵件（唯一）"
    )
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="加密後的密碼"
    )

    # 角色和狀態
    role = Column(
        Enum(UserRole),
        default=UserRole.USER,
        comment="系統角色"
    )
    is_active = Column(
        Boolean,
        default=True,
        comment="帳號是否啟用"
    )

    # 時間戳記
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="建立時間"
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        comment="更新時間"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
