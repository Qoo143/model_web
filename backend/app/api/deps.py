"""
API 依賴注入

提供通用的依賴函數，用於:
- 取得資料庫 Session
- 驗證使用者身份
- 檢查權限
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select


# ============================================
# HTTP Bearer Token 認證方案
# ============================================
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Access Token (從登入 API 取得)"
)


# ============================================
# 資料庫 Session 依賴
# ============================================
async def get_db() -> Generator[AsyncSession, None, None]:
    """
    取得資料庫 Session

    業務邏輯：
    - 每個請求建立一個新的 Session
    - 請求結束後自動關閉
    - 發生錯誤時回滾事務

    使用方式：
    @app.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================
# JWT Token 驗證依賴
# ============================================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    從 JWT Token 取得當前使用者

    業務邏輯：
    1. 從 Authorization Header 取得 Token
    2. 驗證 Token 簽名和過期時間
    3. 從 Token 中取得 user_id
    4. 從資料庫查詢使用者
    5. 檢查使用者是否啟用

    錯誤處理：
    - Token 無效 → 401 Unauthorized
    - Token 過期 → 401 Unauthorized
    - 使用者不存在 → 401 Unauthorized
    - 使用者被停用 → 403 Forbidden

    使用方式：
    @app.get("/me")
    async def get_me(current_user: User = Depends(get_current_user)):
        return current_user
    """
    # 定義認證失敗的例外
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無效的認證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 取得 Token
        token = credentials.credentials

        # 解碼 JWT Token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # 取得 user_id
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # 轉換為整數
        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    # 從資料庫查詢使用者
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # 檢查使用者是否啟用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="使用者帳號已被停用"
        )

    return user


# ============================================
# 權限檢查依賴
# ============================================
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    取得啟用的使用者

    業務邏輯：
    - 確保使用者帳號是啟用狀態
    - 實際上在 get_current_user 已經檢查過了
    - 保留這個函數是為了語意更清楚

    使用方式：
    @app.post("/documents")
    async def upload_document(current_user: User = Depends(get_current_active_user)):
        ...
    """
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    取得管理員使用者

    業務邏輯：
    - 確保使用者是管理員角色
    - 用於需要管理員權限的 API

    使用方式：
    @app.delete("/users/{user_id}")
    async def delete_user(
        user_id: int,
        current_admin: User = Depends(get_current_admin_user)
    ):
        ...
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理員權限"
        )
    return current_user


# ============================================
# 可選的使用者依賴
# ============================================
async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    可選的使用者認證

    業務邏輯：
    - 如果提供 Token 則驗證
    - 如果沒有提供 Token 則返回 None
    - 用於部分公開、部分需要登入的 API

    使用方式：
    @app.get("/documents")
    async def list_documents(
        current_user: Optional[User] = Depends(get_optional_current_user)
    ):
        if current_user:
            # 顯示使用者自己的文件
            pass
        else:
            # 顯示公開文件
            pass
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
