"""
Alembic 環境配置

負責:
- 讀取資料庫連線配置
- 載入所有模型（用於自動生成遷移）
- 提供同步和非同步的遷移支援
"""

from logging.config import fileConfig
import asyncio
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ============================================
# 匯入應用程式配置和模型
# ============================================
import sys
from os.path import dirname, abspath

# 將 backend 目錄加入 Python path
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from app.core.config import settings
from app.core.database import Base

# 匯入所有模型 (確保 Alembic 能偵測到所有表格)
from app.models.user import User
from app.models.group import Group, GroupMember
from app.models.document import Document

# ============================================
# Alembic Config 物件
# ============================================
config = context.config

# 設定資料庫 URL (從 settings 讀取)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 日誌配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData 物件 (包含所有表格定義)
target_metadata = Base.metadata


# ============================================
# 離線模式遷移 (生成 SQL 腳本)
# ============================================
def run_migrations_offline() -> None:
    """
    離線模式遷移

    使用場景:
    - 生成 SQL 腳本而不執行
    - 手動審查遷移 SQL
    - 在沒有資料庫連線的環境中生成腳本

    執行方式:
    alembic upgrade head --sql > migration.sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================
# 線上模式遷移 (直接執行)
# ============================================
def do_run_migrations(connection: Connection) -> None:
    """
    執行遷移腳本

    Args:
        connection: 資料庫連線
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    非同步模式遷移

    使用 asyncmy 驅動進行非同步資料庫操作

    優點:
    - 與應用程式的非同步模式一致
    - 更好的效能
    - 避免阻塞
    """
    # 建立非同步引擎配置
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 遷移時不使用連線池
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    線上模式遷移

    使用場景:
    - 直接對資料庫執行遷移
    - 開發環境快速迭代
    - CI/CD 自動部署

    執行方式:
    alembic upgrade head
    """
    asyncio.run(run_async_migrations())


# ============================================
# 主執行邏輯
# ============================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
