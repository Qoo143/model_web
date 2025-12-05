"""
Google Gemini LLM 服務

整合 Google Gemini API
"""

import time
import httpx
from typing import Optional, List, AsyncGenerator

from app.services.llm.base import BaseLLMService, LLMResponse, Message
from app.core.config import settings


class GeminiService(BaseLLMService):
    """
    Google Gemini LLM 服務

    業務邏輯：
    - 連接 Google Gemini API
    - 支援 Gemini Pro, Gemini Flash 等模型
    - 提供流式和非流式生成

    配置：
    - GEMINI_API_KEY: API 金鑰
    - GEMINI_MODEL: 預設模型
    - GEMINI_TEMPERATURE: 生成溫度
    """

    # Gemini API 基礎 URL
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        api_key: str = None,
        timeout: float = 60.0,
        **kwargs
    ):
        """
        初始化 Gemini 服務

        Args:
            model: 模型名稱（預設從設定讀取）
            temperature: 生成溫度
            api_key: Gemini API 金鑰
            timeout: 請求超時時間（秒）
        """
        super().__init__(
            model=model or settings.GEMINI_MODEL,
            temperature=temperature if temperature is not None else settings.GEMINI_TEMPERATURE,
            **kwargs
        )
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未設定")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """非同步生成回應"""
        messages = []

        if system_prompt:
            messages.append(Message(role="user", content=f"[System Instructions]\n{system_prompt}"))
            messages.append(Message(role="model", content="Understood. I will follow these instructions."))

        messages.append(Message(role="user", content=prompt))

        return await self.chat(messages, **kwargs)

    async def chat(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """非同步多輪對話"""
        start_time = time.time()

        # 轉換訊息格式
        contents = self._convert_messages(messages)

        # 建立請求
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.temperature),
                "topP": kwargs.get("top_p", 0.95),
                "topK": kwargs.get("top_k", 40),
            }
        }

        if self.max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = self.max_tokens

        # 發送請求
        model_name = kwargs.get("model", self.model)
        url = f"{self.BASE_URL}/models/{model_name}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        generation_time = time.time() - start_time

        # 解析回應
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("Gemini API 未返回回應")

        content = ""
        for part in candidates[0].get("content", {}).get("parts", []):
            content += part.get("text", "")

        # Token 統計
        usage_metadata = data.get("usageMetadata", {})
        prompt_tokens = usage_metadata.get("promptTokenCount")
        completion_tokens = usage_metadata.get("candidatesTokenCount")
        total_tokens = usage_metadata.get("totalTokenCount")

        return LLMResponse(
            content=content,
            model=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            generation_time=generation_time,
            finish_reason=candidates[0].get("finishReason", "STOP"),
            metadata={
                "safety_ratings": candidates[0].get("safetyRatings", [])
            }
        )

    def _convert_messages(self, messages: List[Message]) -> List[dict]:
        """將訊息轉換為 Gemini API 格式"""
        contents = []

        for msg in messages:
            # Gemini 使用 "user" 和 "model" 作為角色
            role = "model" if msg.role == "assistant" else "user"

            # 系統訊息需要特殊處理
            if msg.role == "system":
                # 將系統訊息轉換為使用者訊息
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"[System Instructions]\n{msg.content}"}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Understood. I will follow these instructions."}]
                })
            else:
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })

        return contents

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """串流生成回應"""
        messages = []

        if system_prompt:
            messages.append(Message(role="user", content=f"[System Instructions]\n{system_prompt}"))
            messages.append(Message(role="model", content="Understood. I will follow these instructions."))

        messages.append(Message(role="user", content=prompt))

        # 轉換訊息格式
        contents = self._convert_messages(messages)

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", self.temperature),
                "topP": kwargs.get("top_p", 0.95),
                "topK": kwargs.get("top_k", 40),
            }
        }

        if self.max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = self.max_tokens

        model_name = kwargs.get("model", self.model)
        url = f"{self.BASE_URL}/models/{model_name}:streamGenerateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        # Gemini 串流回應格式可能包含多個 JSON 物件
                        try:
                            # 移除可能的前綴
                            if line.startswith("data: "):
                                line = line[6:]
                            data = json.loads(line)
                            candidates = data.get("candidates", [])
                            if candidates:
                                for part in candidates[0].get("content", {}).get("parts", []):
                                    text = part.get("text", "")
                                    if text:
                                        yield text
                        except json.JSONDecodeError:
                            continue

    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            # 發送一個簡單的請求來檢查 API 可用性
            url = f"{self.BASE_URL}/models/{self.model}?key={self.api_key}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """列出可用模型"""
        try:
            url = f"{self.BASE_URL}/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return [
                    model["name"].replace("models/", "")
                    for model in data.get("models", [])
                    if "generateContent" in model.get("supportedGenerationMethods", [])
                ]
        except Exception:
            return []
