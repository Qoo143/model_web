"""
向量資料庫服務

管理 Chroma 向量資料庫的操作
"""

import httpx
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class SearchResult:
    """搜尋結果"""
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float  # 相似度分數（越高越相似）


class VectorStoreService:
    """
    向量資料庫服務

    業務邏輯：
    - 使用 Chroma 作為向量資料庫
    - 支援 HTTP API 模式（獨立部署）
    - 管理 collection 和文件向量

    配置：
    - CHROMA_HOST: Chroma 伺服器地址
    - CHROMA_PORT: Chroma 伺服器埠口
    - CHROMA_COLLECTION_NAME: 預設 collection 名稱
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = None,
        timeout: float = 30.0
    ):
        """
        初始化向量資料庫服務

        Args:
            host: Chroma 伺服器地址
            port: Chroma 伺服器埠口
            collection_name: Collection 名稱
            timeout: 請求超時時間（秒）
        """
        self.host = host or settings.CHROMA_HOST
        self.port = port or settings.CHROMA_PORT
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.timeout = timeout
        self.base_url = f"http://{self.host}:{self.port}"
        self._collection_id = None

    async def _ensure_collection(self) -> str:
        """確保 collection 存在，返回 collection ID"""
        if self._collection_id:
            return self._collection_id

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 嘗試取得現有 collection
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/collections/{self.collection_name}"
                )
                if response.status_code == 200:
                    data = response.json()
                    self._collection_id = data.get("id")
                    return self._collection_id
            except Exception:
                pass

            # 建立新 collection
            response = await client.post(
                f"{self.base_url}/api/v1/collections",
                json={
                    "name": self.collection_name,
                    "metadata": {"description": "Library RAG documents"}
                }
            )
            response.raise_for_status()
            data = response.json()
            self._collection_id = data.get("id")
            return self._collection_id

    async def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        新增文件到向量資料庫

        Args:
            ids: 文件 ID 列表
            embeddings: 向量列表
            documents: 原始文本列表
            metadatas: 元資料列表

        Returns:
            bool: 是否成功
        """
        await self._ensure_collection()

        payload = {
            "ids": ids,
            "embeddings": embeddings,
            "documents": documents,
        }

        if metadatas:
            payload["metadatas"] = metadatas

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/collections/{self._collection_id}/add",
                json=payload
            )
            response.raise_for_status()
            return True

    async def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: List[str] = None
    ) -> List[SearchResult]:
        """
        查詢相似文件

        Args:
            query_embedding: 查詢向量
            n_results: 返回結果數量
            where: 過濾條件
            include: 返回的欄位

        Returns:
            List[SearchResult]: 搜尋結果列表
        """
        await self._ensure_collection()

        payload = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": include or ["documents", "metadatas", "distances"]
        }

        if where:
            payload["where"] = where

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/collections/{self._collection_id}/query",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

        # 解析結果
        results = []
        ids = data.get("ids", [[]])[0]
        documents = data.get("documents", [[]])[0]
        metadatas = data.get("metadatas", [[]])[0]
        distances = data.get("distances", [[]])[0]

        for i, doc_id in enumerate(ids):
            # 將距離轉換為相似度分數（1 - distance）
            # Chroma 預設使用 L2 距離，較小的距離表示更相似
            score = 1.0 / (1.0 + distances[i]) if distances else 0.0

            results.append(SearchResult(
                id=doc_id,
                content=documents[i] if i < len(documents) else "",
                metadata=metadatas[i] if i < len(metadatas) else {},
                score=score
            ))

        return results

    async def delete_by_ids(self, ids: List[str]) -> bool:
        """
        根據 ID 刪除文件

        Args:
            ids: 要刪除的文件 ID 列表

        Returns:
            bool: 是否成功
        """
        await self._ensure_collection()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/collections/{self._collection_id}/delete",
                json={"ids": ids}
            )
            response.raise_for_status()
            return True

    async def delete_by_filter(self, where: Dict[str, Any]) -> bool:
        """
        根據條件刪除文件

        Args:
            where: 過濾條件（例如 {"document_id": 1}）

        Returns:
            bool: 是否成功
        """
        await self._ensure_collection()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v1/collections/{self._collection_id}/delete",
                json={"where": where}
            )
            response.raise_for_status()
            return True

    async def count(self) -> int:
        """取得文件數量"""
        await self._ensure_collection()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/collections/{self._collection_id}/count"
            )
            response.raise_for_status()
            return response.json()

    async def health_check(self) -> bool:
        """健康檢查"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/heartbeat"
                )
                return response.status_code == 200
        except Exception:
            return False


# 單例實例
vectorstore_service = VectorStoreService()
