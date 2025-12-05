"""
LLM 服務工廠

根據配置選擇適當的 LLM 服務
"""

from typing import Optional
from app.services.llm.base import BaseLLMService
from app.services.llm.ollama_service import OllamaService
from app.services.llm.gemini_service import GeminiService
from app.core.config import settings


class LLMFactory:
    """
    LLM 服務工廠

    業務邏輯：
    - 根據 LLM_PROVIDER 設定選擇服務
    - 支援 ollama 和 gemini 兩種提供者
    - 提供統一的介面取得 LLM 服務
    """

    _instance: Optional[BaseLLMService] = None

    @classmethod
    def create(
        cls,
        provider: str = None,
        **kwargs
    ) -> BaseLLMService:
        """
        建立 LLM 服務

        Args:
            provider: LLM 提供者 ("ollama" 或 "gemini")
            **kwargs: 額外參數傳遞給服務

        Returns:
            BaseLLMService: LLM 服務實例

        Raises:
            ValueError: 不支援的提供者
        """
        provider = (provider or settings.LLM_PROVIDER).lower()

        if provider == "ollama":
            return OllamaService(**kwargs)
        elif provider == "gemini":
            return GeminiService(**kwargs)
        else:
            raise ValueError(
                f"不支援的 LLM 提供者: {provider}。"
                f"支援的選項: ollama, gemini"
            )

    @classmethod
    def get_default(cls) -> BaseLLMService:
        """
        取得預設的 LLM 服務（單例）

        Returns:
            BaseLLMService: LLM 服務實例
        """
        if cls._instance is None:
            cls._instance = cls.create()
        return cls._instance

    @classmethod
    def reset(cls):
        """重置單例實例（用於測試）"""
        cls._instance = None

    @classmethod
    def get_available_providers(cls) -> list:
        """取得可用的提供者列表"""
        providers = ["ollama"]

        # 檢查 Gemini API Key 是否設定
        if settings.GEMINI_API_KEY:
            providers.append("gemini")

        return providers


def get_llm_service(provider: str = None) -> BaseLLMService:
    """
    取得 LLM 服務的便捷函數

    Args:
        provider: LLM 提供者（可選）

    Returns:
        BaseLLMService: LLM 服務實例
    """
    if provider:
        return LLMFactory.create(provider=provider)
    return LLMFactory.get_default()
