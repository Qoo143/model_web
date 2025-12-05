"""
文件處理協調器

協調文件的解析、分塊和向量化流程
"""

import asyncio
from typing import Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.document import Document, DocumentStatus
from app.services.document.parser import DocumentParser, ParsedDocument
from app.services.document.chunker import TextChunker, TextChunk
from app.core.config import settings


@dataclass
class ProcessingResult:
    """處理結果"""
    success: bool
    document_id: int
    chunk_count: int = 0
    error_message: Optional[str] = None
    chunks: Optional[List[TextChunk]] = None


class DocumentProcessor:
    """
    文件處理協調器

    業務邏輯：
    1. 解析文件內容
    2. 將內容分塊
    3. （Phase 3）向量化並存入 Chroma
    4. 更新文件狀態

    處理流程：
    pending -> processing -> completed/failed
    """

    def __init__(
        self,
        parser: Optional[DocumentParser] = None,
        chunker: Optional[TextChunker] = None
    ):
        self.parser = parser or DocumentParser()
        self.chunker = chunker or TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    async def process_document(
        self,
        db: AsyncSession,
        document_id: int,
        on_progress: Optional[Callable[[int, str], None]] = None
    ) -> ProcessingResult:
        """
        處理單個文件

        Args:
            db: 資料庫 session
            document_id: 文件 ID
            on_progress: 進度回調函數 (progress: 0-100, message: str)

        Returns:
            ProcessingResult: 處理結果
        """
        # 1. 查詢文件
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            return ProcessingResult(
                success=False,
                document_id=document_id,
                error_message="文件不存在"
            )

        try:
            # 2. 更新狀態為處理中
            document.processing_status = DocumentStatus.PROCESSING
            await db.commit()

            if on_progress:
                on_progress(10, "開始解析文件")

            # 3. 解析文件
            parsed = self.parser.parse(document.file_path)

            if on_progress:
                on_progress(30, "文件解析完成，開始分塊")

            # 4. 分塊
            metadata = {
                "document_id": document.id,
                "group_id": document.group_id,
                "filename": document.original_filename,
                "file_type": document.file_type
            }
            chunks = self.chunker.split(parsed.content, metadata)

            if on_progress:
                on_progress(50, f"分塊完成，共 {len(chunks)} 個塊")

            # 5. TODO: 向量化並存入 Chroma (Phase 3)
            # await self._vectorize_chunks(chunks, document)

            if on_progress:
                on_progress(90, "向量化完成")

            # 6. 更新文件狀態
            document.processing_status = DocumentStatus.COMPLETED
            document.chunk_count = len(chunks)
            document.page_count = parsed.line_count // 50 + 1  # 估算頁數
            await db.commit()

            if on_progress:
                on_progress(100, "處理完成")

            return ProcessingResult(
                success=True,
                document_id=document_id,
                chunk_count=len(chunks),
                chunks=chunks
            )

        except Exception as e:
            # 處理失敗
            document.processing_status = DocumentStatus.FAILED
            document.error_message = str(e)
            await db.commit()

            return ProcessingResult(
                success=False,
                document_id=document_id,
                error_message=str(e)
            )

    async def process_documents_batch(
        self,
        db: AsyncSession,
        document_ids: List[int]
    ) -> List[ProcessingResult]:
        """
        批次處理多個文件

        Args:
            db: 資料庫 session
            document_ids: 文件 ID 列表

        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        results = []
        for doc_id in document_ids:
            result = await self.process_document(db, doc_id)
            results.append(result)
        return results

    async def reprocess_failed_documents(
        self,
        db: AsyncSession,
        group_id: Optional[int] = None
    ) -> List[ProcessingResult]:
        """
        重新處理失敗的文件

        Args:
            db: 資料庫 session
            group_id: 可選的群組 ID 篩選

        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        # 查詢失敗的文件
        query = select(Document).where(
            Document.processing_status == DocumentStatus.FAILED
        )
        if group_id:
            query = query.where(Document.group_id == group_id)

        result = await db.execute(query)
        failed_docs = result.scalars().all()

        # 重新處理
        return await self.process_documents_batch(
            db,
            [doc.id for doc in failed_docs]
        )

    def get_chunks_preview(
        self,
        file_path: str,
        max_chunks: int = 5
    ) -> List[dict]:
        """
        取得文件分塊預覽（不存入資料庫）

        用於測試和調試

        Args:
            file_path: 文件路徑
            max_chunks: 最大返回塊數

        Returns:
            List[dict]: 塊資訊列表
        """
        parsed = self.parser.parse(file_path)
        chunks = self.chunker.split(parsed.content)

        return [
            {
                "index": chunk.chunk_index,
                "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "length": len(chunk.content),
                "start": chunk.start_char,
                "end": chunk.end_char
            }
            for chunk in chunks[:max_chunks]
        ]


# 單例實例
processor = DocumentProcessor()
