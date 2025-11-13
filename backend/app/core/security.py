"""
安全相關功能

包含密碼加密、JWT Token 生成與驗證
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from app.core.config import settings


# ============================================
# 密碼加密配置
# ============================================
# 使用 bcrypt 演算法進行密碼加密
# bcrypt 特性:
# - 單向加密（無法反推原始密碼）
# - 自動加鹽（相同密碼每次加密結果不同）
# - 慢速演算法（防止暴力破解）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    加密密碼

    業務邏輯:
    - 使用 bcrypt 演算法
    - 自動生成隨機鹽值
    - 返回加密後的 hash

    Args:
        password: 明文密碼

    Returns:
        加密後的密碼 hash

    範例:
        >>> hash_password("password123")
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NAuJC6eJWJfC'
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼

    業務邏輯:
    - 將明文密碼和資料庫中的 hash 比對
    - bcrypt 會自動處理鹽值

    Args:
        plain_password: 使用者輸入的明文密碼
        hashed_password: 資料庫中儲存的 hash

    Returns:
        是否匹配

    範例:
        >>> hashed = hash_password("password123")
        >>> verify_password("password123", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================
# JWT Token 處理
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT Access Token

    業務邏輯:
    - 將使用者資訊編碼成 JWT
    - 設定過期時間
    - 使用密鑰簽章（防止偽造）

    Args:
        data: 要編碼的資料，通常包含:
            - user_id: 使用者 ID
            - username: 使用者名稱
            - role: 使用者角色
        expires_delta: 過期時間（可選）

    Returns:
        JWT Token 字串

    範例:
        >>> token = create_access_token({"user_id": 1, "username": "alice"})
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()

    # 設定過期時間
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # 將過期時間加入 payload
    to_encode.update({"exp": expire})

    # 編碼成 JWT
    # - 使用 SECRET_KEY 簽章
    # - 使用 HS256 演算法
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解碼並驗證 JWT Token

    業務邏輯:
    - 使用密鑰驗證簽章
    - 檢查是否過期
    - 返回 payload 資料

    Args:
        token: JWT Token 字串

    Returns:
        解碼後的 payload（dict），如果無效則返回 None

    可能的錯誤:
    - JWTError: Token 格式錯誤
    - ExpiredSignatureError: Token 已過期
    - JWTClaimsError: Claims 驗證失敗

    範例:
        >>> token = create_access_token({"user_id": 1})
        >>> payload = decode_access_token(token)
        >>> print(payload['user_id'])
        1
    """
    try:
        # 解碼 JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Token 無效或過期
        return None
