"""
LLM 服務抽象基類

定義 LLM 服務的統一介面，便於切換不同的 LLM 提供者
"""

from abc import ABC, abstractmethod
from typing import Optional, List, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LLMResponse:
    """LLM 回應資料"""
    content: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    generation_time: Optional[float] = None
    finish_reason: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Message:
    """對話訊息"""
    role: str  # "system", "user", "assistant"
    content: str


class BaseLLMService(ABC):
    """
    LLM 服務抽象基類

    業務邏輯：
    - 提供統一的 LLM 呼叫介面
    - 支援同步和非同步生成
    - 支援串流輸出
    - 記錄使用統計

    子類需要實作：
    - generate(): 同步生成
    - generate_async(): 非同步生成
    - stream(): 串流生成
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        初始化 LLM 服務

        Args:
            model: 模型名稱
            temperature: 生成溫度 (0.0-1.0)
            max_tokens: 最大生成 token 數
            **kwargs: 其他參數
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra_params = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        非同步生成回應

        Args:
            prompt: 使用者提示
            system_prompt: 系統提示
            **kwargs: 額外參數

        Returns:
            LLMResponse: 生成結果
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """
        非同步多輪對話

        Args:
            messages: 對話歷史
            **kwargs: 額外參數

        Returns:
            LLMResponse: 生成結果
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        串流生成回應

        Args:
            prompt: 使用者提示
            system_prompt: 系統提示
            **kwargs: 額外參數

        Yields:
            str: 生成的文字片段
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        健康檢查

        Returns:
            bool: 服務是否可用
        """
        pass

    def get_model_info(self) -> dict:
        """取得模型資訊"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": self.__class__.__name__
        }
