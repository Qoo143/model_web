"""
資料庫連線配置

提供 SQLAlchemy 非同步引擎和 Session 管理
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings


# ============================================
# 建立非同步資料庫引擎
# ============================================
# 使用 aiomysql 驅動實現非同步操作
# 優點:
# - 不會阻塞其他請求
# - 提高併發處理能力
# - 更好的效能
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 開發模式顯示 SQL 語句
    pool_pre_ping=True,   # 連線前檢查是否有效（避免斷線）
    pool_size=10,         # 連線池大小
    max_overflow=20,      # 最大溢出連線數
    pool_recycle=3600     # 連線回收時間（秒）
)


# ============================================
# Session 工廠
# ============================================
# 用於建立資料庫 Session
# 每個請求會獲得獨立的 Session
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # commit 後物件仍然可用
    autocommit=False,        # 手動控制 commit
    autoflush=False          # 手動控制 flush
)


# ============================================
# Base 類別
# ============================================
# 所有資料庫模型（Model）都繼承此類別
# 提供:
# - 自動表格生成
# - ORM 功能
# - 查詢 API
Base = declarative_base()


# ============================================
# 依賴注入：取得資料庫 Session
# ============================================
async def get_db() -> AsyncSession:
    """
    資料庫 Session 依賴注入

    業務邏輯:
    1. 建立 Session
    2. yield 給路由函數使用
    3. 請求結束後:
       - 成功: commit
       - 失敗: rollback
       - 最後: close

    使用方式:
    ```python
    @router.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(User))
        users = result.scalars().all()
        return users
    ```

    Yields:
        AsyncSession: 資料庫 Session

    注意事項:
    - 每個請求獨立的 Session
    - 自動處理事務（transaction）
    - 異常時自動 rollback
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # 請求成功，commit 變更
            await session.commit()
        except Exception:
            # 發生錯誤，rollback 避免資料不一致
            await session.rollback()
            raise
        finally:
            # 無論如何都關閉連線
            await session.close()


# ============================================
# 初始化資料庫
# ============================================
async def init_db():
    """
    初始化資料庫

    業務邏輯:
    - 建立所有資料表
    - 僅在開發環境使用
    - 生產環境應使用 Alembic 遷移

    注意:
    - 不會刪除現有資料表
    - 只建立不存在的資料表
    """
    async with engine.begin() as conn:
        # 建立所有繼承 Base 的模型對應的資料表
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    關閉資料庫連線

    業務邏輯:
    - 關閉所有連線池
    - 釋放資源
    - 應用程式關閉時呼叫
    """
    await engine.dispose()
