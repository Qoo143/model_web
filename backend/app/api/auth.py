"""
認證 API 路由

提供使用者註冊、登入、登出功能
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    MessageResponse,
)

# 建立路由器
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


# ============================================
# 註冊 API
# ============================================
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="使用者註冊",
    description="""
    註冊新使用者帳號

    業務邏輯：
    1. 驗證輸入資料（Pydantic 自動驗證）
    2. 檢查使用者名稱和 Email 是否已存在
    3. 加密密碼（bcrypt）
    4. 建立新使用者記錄
    5. 返回使用者資訊（不含密碼）

    錯誤處理：
    - 使用者名稱或 Email 已存在 → 400 Bad Request
    - 資料驗證失敗 → 422 Unprocessable Entity
    """
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """註冊新使用者"""

    # 1. 檢查使用者名稱是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者名稱已被使用"
        )

    # 2. 檢查 Email 是否已存在
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email 已被使用"
        )

    # 3. 建立新使用者
    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password)
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="註冊失敗，請檢查輸入資料"
        )


# ============================================
# 登入 API
# ============================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="使用者登入",
    description="""
    使用者登入取得 JWT Token

    業務邏輯：
    1. 驗證使用者名稱和密碼
    2. 檢查帳號是否啟用
    3. 生成 JWT Access Token
    4. 返回 Token 和使用者資訊

    Token 使用方式：
    - 前端儲存 access_token
    - 後續請求在 Header 中帶上：
      Authorization: Bearer {access_token}

    錯誤處理：
    - 使用者名稱或密碼錯誤 → 401 Unauthorized
    - 帳號被停用 → 403 Forbidden
    """
)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """使用者登入"""

    # 1. 查詢使用者
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalar_one_or_none()

    # 2. 驗證使用者和密碼
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="使用者名稱或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 檢查帳號是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="帳號已被停用"
        )

    # 4. 生成 JWT Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # sub 是 JWT 標準欄位，存放使用者 ID
        expires_delta=access_token_expires
    )

    # 5. 返回 Token 和使用者資訊
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# ============================================
# 取得當前使用者資訊 API
# ============================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="取得當前使用者資訊",
    description="""
    取得當前登入使用者的資訊

    業務邏輯：
    1. 從 JWT Token 解析使用者 ID
    2. 從資料庫查詢使用者資訊
    3. 返回使用者資訊（不含密碼）

    認證：
    - 需要在 Header 帶上 JWT Token
    - Authorization: Bearer {access_token}

    錯誤處理：
    - Token 無效或過期 → 401 Unauthorized
    """
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得當前使用者資訊"""
    return current_user


# ============================================
# 登出 API (可選)
# ============================================
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="使用者登出",
    description="""
    使用者登出

    業務邏輯：
    - JWT Token 是無狀態的，後端不需要做任何處理
    - 前端只需刪除儲存的 Token
    - 這個 API 主要用於記錄登出行為（未來可擴展）

    注意：
    - Token 在過期前仍然有效
    - 如需立即失效，需要實作 Token 黑名單機制
    """
)
async def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """使用者登出"""

    # JWT Token 是無狀態的，後端不需要處理
    # 前端刪除 Token 即可
    # 這裡可以記錄登出行為（未來可擴展）

    return MessageResponse(
        message="登出成功",
        detail=f"使用者 {current_user.username} 已登出"
    )


# ============================================
# 測試認證 API (開發用)
# ============================================
@router.get(
    "/test",
    response_model=MessageResponse,
    summary="測試認證",
    description="測試 JWT Token 認證是否正常運作（開發用）"
)
async def test_auth(
    current_user: User = Depends(get_current_user)
) -> Any:
    """測試認證"""
    return MessageResponse(
        message="認證成功",
        detail=f"當前使用者: {current_user.username} (ID: {current_user.id})"
    )
