"""
Ollama LLM 服務

整合本地運行的 Ollama LLM
"""

import time
import httpx
from typing import Optional, List, AsyncGenerator

from app.services.llm.base import BaseLLMService, LLMResponse, Message
from app.core.config import settings


class OllamaService(BaseLLMService):
    """
    Ollama LLM 服務

    業務邏輯：
    - 連接本地或遠端 Ollama 服務
    - 支援多種開源模型（如 gpt-oss-20b, qwen, llama 等）
    - 提供流式和非流式生成

    配置：
    - OLLAMA_BASE_URL: Ollama 服務地址
    - OLLAMA_MODEL: 預設模型
    - OLLAMA_TEMPERATURE: 生成溫度
    """

    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        base_url: str = None,
        timeout: float = 120.0,
        **kwargs
    ):
        """
        初始化 Ollama 服務

        Args:
            model: 模型名稱（預設從設定讀取）
            temperature: 生成溫度
            base_url: Ollama 服務地址
            timeout: 請求超時時間（秒）
        """
        super().__init__(
            model=model or settings.OLLAMA_MODEL,
            temperature=temperature if temperature is not None else settings.OLLAMA_TEMPERATURE,
            **kwargs
        )
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """非同步生成回應"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return await self._call_chat_api(messages, **kwargs)

    async def chat(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """非同步多輪對話"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        return await self._call_chat_api(formatted_messages, **kwargs)

    async def _call_chat_api(
        self,
        messages: List[dict],
        **kwargs
    ) -> LLMResponse:
        """呼叫 Ollama Chat API"""
        start_time = time.time()

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
            }
        }

        if self.max_tokens:
            payload["options"]["num_predict"] = self.max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        generation_time = time.time() - start_time

        # 解析回應
        message = data.get("message", {})
        content = message.get("content", "")

        # Token 統計（Ollama 提供）
        prompt_tokens = data.get("prompt_eval_count")
        completion_tokens = data.get("eval_count")
        total_tokens = None
        if prompt_tokens and completion_tokens:
            total_tokens = prompt_tokens + completion_tokens

        return LLMResponse(
            content=content,
            model=data.get("model", self.model),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            generation_time=generation_time,
            finish_reason=data.get("done_reason", "stop"),
            metadata={
                "ollama_done": data.get("done", True),
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "eval_duration": data.get("eval_duration"),
            }
        )

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """串流生成回應"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
            }
        }

        if self.max_tokens:
            payload["options"]["num_predict"] = self.max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        message = data.get("message", {})
                        content = message.get("content", "")
                        if content:
                            yield content
                        if data.get("done", False):
                            break

    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """列出可用模型"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []

    async def pull_model(self, model_name: str) -> bool:
        """下載模型"""
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name}
                )
                return response.status_code == 200
        except Exception:
            return False
