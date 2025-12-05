"""
檢索服務

從向量資料庫檢索相關文件
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from app.services.rag.embedder import EmbeddingService, embedding_service
from app.services.rag.vectorstore import VectorStoreService, vectorstore_service, SearchResult
from app.core.config import settings


@dataclass
class RetrievalResult:
    """檢索結果"""
    content: str
    document_id: int
    document_name: str
    chunk_index: int
    score: float
    metadata: Dict[str, Any]


class RetrieverService:
    """
    檢索服務

    業務邏輯：
    - 將查詢轉換為向量
    - 從向量資料庫檢索相關文件
    - 支援文件過濾和權限控制
    - 返回排序後的結果

    配置：
    - TOP_K_RETRIEVAL: 返回的文件數量
    """

    def __init__(
        self,
        embedding_service: EmbeddingService = None,
        vectorstore_service: VectorStoreService = None,
        top_k: int = None
    ):
        """
        初始化檢索服務

        Args:
            embedding_service: Embedding 服務
            vectorstore_service: 向量資料庫服務
            top_k: 返回的文件數量
        """
        self.embedding = embedding_service or embedding_service
        self.vectorstore = vectorstore_service or vectorstore_service
        self.top_k = top_k or settings.TOP_K_RETRIEVAL

    async def retrieve(
        self,
        query: str,
        top_k: int = None,
        document_ids: Optional[List[int]] = None,
        group_id: Optional[int] = None,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """
        檢索相關文件

        Args:
            query: 查詢文本
            top_k: 返回數量（覆蓋預設值）
            document_ids: 限制在這些文件中搜尋
            group_id: 限制在此群組中搜尋
            min_score: 最低相似度分數

        Returns:
            List[RetrievalResult]: 檢索結果列表
        """
        k = top_k or self.top_k

        # 1. 將查詢轉換為向量
        query_embedding = await self.embedding.embed_query(query)

        # 2. 建立過濾條件
        where = self._build_filter(document_ids, group_id)

        # 3. 從向量資料庫查詢
        search_results = await self.vectorstore.query(
            query_embedding=query_embedding,
            n_results=k * 2,  # 多查一些以便過濾
            where=where
        )

        # 4. 過濾和轉換結果
        results = []
        for sr in search_results:
            if sr.score < min_score:
                continue

            results.append(RetrievalResult(
                content=sr.content,
                document_id=sr.metadata.get("document_id", 0),
                document_name=sr.metadata.get("filename", ""),
                chunk_index=sr.metadata.get("chunk_index", 0),
                score=sr.score,
                metadata=sr.metadata
            ))

        # 5. 按分數排序並限制數量
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:k]

    def _build_filter(
        self,
        document_ids: Optional[List[int]],
        group_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """建立過濾條件"""
        conditions = []

        if document_ids:
            conditions.append({
                "document_id": {"$in": document_ids}
            })

        if group_id:
            conditions.append({
                "group_id": {"$eq": group_id}
            })

        if not conditions:
            return None

        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}

    async def retrieve_for_documents(
        self,
        query: str,
        document_ids: List[int],
        top_k: int = None
    ) -> List[RetrievalResult]:
        """
        在指定文件中檢索

        便捷方法，用於使用者選擇特定文件的情況

        Args:
            query: 查詢文本
            document_ids: 文件 ID 列表
            top_k: 返回數量

        Returns:
            List[RetrievalResult]: 檢索結果列表
        """
        return await self.retrieve(
            query=query,
            top_k=top_k,
            document_ids=document_ids
        )

    async def retrieve_for_group(
        self,
        query: str,
        group_id: int,
        top_k: int = None
    ) -> List[RetrievalResult]:
        """
        在指定群組中檢索

        便捷方法，用於在整個群組的文件中搜尋

        Args:
            query: 查詢文本
            group_id: 群組 ID
            top_k: 返回數量

        Returns:
            List[RetrievalResult]: 檢索結果列表
        """
        return await self.retrieve(
            query=query,
            top_k=top_k,
            group_id=group_id
        )


# 單例實例
retriever_service = RetrieverService()
