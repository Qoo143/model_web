"""
Embedding 服務

將文本轉換為向量表示
"""

import httpx
from typing import List, Optional
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class EmbeddingResult:
    """Embedding 結果"""
    embeddings: List[List[float]]
    model: str
    dimensions: int


class EmbeddingService:
    """
    Embedding 服務

    業務邏輯：
    - 使用 Ollama 的 embedding API（支援 BGE-M3 等模型）
    - 批量處理文本以提高效率
    - 支援中英文混合文本

    配置：
    - EMBEDDING_MODEL: Embedding 模型名稱
    - OLLAMA_BASE_URL: Ollama 服務地址

    注意：
    - BGE-M3 模型需要先透過 ollama pull nomic-embed-text 或類似命令下載
    - 也可使用 Ollama 支援的其他 embedding 模型
    """

    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        timeout: float = 60.0
    ):
        """
        初始化 Embedding 服務

        Args:
            model: Embedding 模型名稱
            base_url: Ollama 服務地址
            timeout: 請求超時時間（秒）
        """
        self.model = model or settings.EMBEDDING_MODEL
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = timeout

        # 預設維度（根據模型不同可能需要調整）
        self._dimensions = 1024  # BGE-M3 預設維度

    async def embed_text(self, text: str) -> List[float]:
        """
        將單個文本轉換為向量

        Args:
            text: 要轉換的文本

        Returns:
            List[float]: 向量表示
        """
        result = await self.embed_texts([text])
        return result.embeddings[0]

    async def embed_texts(self, texts: List[str]) -> EmbeddingResult:
        """
        批量將文本轉換為向量

        Args:
            texts: 文本列表

        Returns:
            EmbeddingResult: 包含所有向量的結果
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=self.model,
                dimensions=self._dimensions
            )

        embeddings = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for text in texts:
                # Ollama embedding API
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                data = response.json()

                # 回應格式: {"embedding": [...]}
                embedding = data.get("embedding", [])
                embeddings.append(embedding)

                # 更新維度資訊
                if embedding and self._dimensions != len(embedding):
                    self._dimensions = len(embedding)

        return EmbeddingResult(
            embeddings=embeddings,
            model=self.model,
            dimensions=self._dimensions
        )

    async def embed_query(self, query: str) -> List[float]:
        """
        將查詢文本轉換為向量

        與 embed_text 相同，但語意上用於查詢
        某些 embedding 模型對查詢和文件有不同處理

        Args:
            query: 查詢文本

        Returns:
            List[float]: 向量表示
        """
        return await self.embed_text(query)

    @property
    def dimensions(self) -> int:
        """取得向量維度"""
        return self._dimensions

    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            # 嘗試生成一個簡單的 embedding
            await self.embed_text("test")
            return True
        except Exception:
            return False


# 單例實例
embedding_service = EmbeddingService()
