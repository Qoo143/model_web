"""
應用程式配置

從環境變數讀取配置，提供型別安全的配置管理
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    應用程式配置類別

    業務邏輯:
    - 從環境變數讀取配置
    - 提供預設值
    - 型別驗證

    優先級: 環境變數 > .env 檔案 > 預設值
    """

    # ============================================
    # 應用程式基本配置
    # ============================================
    APP_NAME: str = "Library RAG Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ============================================
    # 資料庫配置 (拆分為獨立環境變數)
    # ============================================
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "library_user"
    DB_PASSWORD: str = "library_pass"
    DB_NAME: str = "library_agent"

    @property
    def DATABASE_URL(self) -> str:
        """
        動態構建資料庫連線字串

        使用 asyncmy 驅動 (aiomysql 的替代方案，更好的 async 支援)
        格式: mysql+asyncmy://使用者:密碼@主機:埠/資料庫名稱
        """
        return f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # ============================================
    # JWT 認證配置
    # ============================================
    SECRET_KEY: str  # 必須從環境變數提供，不設定預設值以提升安全性
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ============================================
    # LLM 提供者選擇
    # ============================================
    LLM_PROVIDER: str = "ollama"  # ollama 或 gemini

    # ============================================
    # Ollama LLM 配置 (本地模型)
    # ============================================
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "gpt-oss-20b"
    OLLAMA_TEMPERATURE: float = 0.3  # 0.0 = 確定性, 1.0 = 創造性

    # ============================================
    # Gemini API 配置 (雲端模型)
    # ============================================
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_TEMPERATURE: float = 0.3

    # ============================================
    # Embedding 模型配置
    # ============================================
    EMBEDDING_MODEL: str = "nomic-embed-text"  # Ollama 模型名稱
    EMBEDDING_DEVICE: str = "cpu"  # cpu 或 cuda

    # ============================================
    # Chroma 向量資料庫配置 (伺服器模式)
    # ============================================
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_NAME: str = "library_documents"

    @property
    def CHROMA_SERVER_URL(self) -> str:
        """
        Chroma 伺服器連線 URL

        伺服器模式優點:
        - 資料集中管理
        - 多個後端實例可共用同一向量庫
        - 更好的效能和擴展性
        """
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"

    # ============================================
    # 文件上傳配置 (簡化：僅支援純文字格式)
    # ============================================
    UPLOAD_DIR: str = "./storage/documents"
    MAX_FILE_SIZE: int = 10485760  # 10MB (bytes) - 純文字檔案通常較小
    ALLOWED_FILE_TYPES: set = {"txt", "md"}  # 僅支援 txt 和 markdown

    # ============================================
    # RAG 配置
    # ============================================
    CHUNK_SIZE: int = 500  # 每個 chunk 的字元數
    CHUNK_OVERLAP: int = 50  # chunk 之間的重疊字元數
    TOP_K_RETRIEVAL: int = 5  # 檢索時返回的文件數量

    # ============================================
    # CORS 配置
    # ============================================
    CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        case_sensitive = True


# 單例模式：全域配置實例
settings = Settings()
