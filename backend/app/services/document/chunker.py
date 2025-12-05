"""
文本分塊器

將長文本切割成適合向量化的小塊
使用語意分塊策略，保持文本的語意完整性
"""

import re
from typing import List, Optional
from dataclasses import dataclass
from app.core.config import settings


@dataclass
class TextChunk:
    """文本塊"""
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Optional[dict] = None


class TextChunker:
    """
    文本分塊器

    業務邏輯：
    - 按照自然語言邊界切割文本
    - 使用重疊窗口保持上下文
    - 優先在段落、句子邊界切割
    - 避免切斷詞語

    分隔符優先級：
    1. 連續換行（段落）
    2. 單個換行
    3. 句號、問號、驚嘆號
    4. 逗號、分號
    5. 空格
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        """
        初始化分塊器

        Args:
            chunk_size: 每個塊的最大字元數
            chunk_overlap: 塊之間的重疊字元數
            separators: 分隔符列表（按優先級排序）
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = separators or [
            "\n\n",   # 段落分隔
            "\n",     # 行分隔
            "。",     # 中文句號
            ".",      # 英文句號
            "？",     # 中文問號
            "?",      # 英文問號
            "！",     # 中文驚嘆號
            "!",      # 英文驚嘆號
            "；",     # 中文分號
            ";",      # 英文分號
            "，",     # 中文逗號
            ",",      # 英文逗號
            " ",      # 空格
        ]

    def split(self, text: str, metadata: Optional[dict] = None) -> List[TextChunk]:
        """
        將文本切割成塊

        Args:
            text: 要切割的文本
            metadata: 附加到每個塊的元數據

        Returns:
            List[TextChunk]: 文本塊列表
        """
        if not text or not text.strip():
            return []

        # 清理文本
        text = self._clean_text(text)

        # 遞歸切割
        chunks_text = self._recursive_split(text, self.separators)

        # 合併過小的塊
        merged_chunks = self._merge_small_chunks(chunks_text)

        # 建立 TextChunk 物件
        result = []
        current_pos = 0

        for idx, chunk_text in enumerate(merged_chunks):
            # 找到這個塊在原文中的位置
            start_pos = text.find(chunk_text, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            chunk = TextChunk(
                content=chunk_text,
                chunk_index=idx,
                start_char=start_pos,
                end_char=start_pos + len(chunk_text),
                metadata=metadata.copy() if metadata else None
            )
            result.append(chunk)
            current_pos = start_pos + len(chunk_text) - self.chunk_overlap

        return result

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多餘的空白
        text = re.sub(r" +", " ", text)
        # 移除多餘的換行
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _recursive_split(
        self,
        text: str,
        separators: List[str]
    ) -> List[str]:
        """
        遞歸切割文本

        嘗試使用當前分隔符切割，如果結果仍然太大，
        則使用下一個分隔符繼續切割
        """
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        if not separators:
            # 沒有更多分隔符，強制切割
            return self._force_split(text)

        separator = separators[0]
        remaining_separators = separators[1:]

        # 使用當前分隔符切割
        parts = text.split(separator)

        result = []
        current_chunk = ""

        for i, part in enumerate(parts):
            if not part.strip():
                continue

            # 加上分隔符（除了最後一個部分）
            part_with_sep = part + (separator if i < len(parts) - 1 else "")

            # 檢查是否可以加入當前塊
            potential_chunk = current_chunk + part_with_sep

            if len(potential_chunk) <= self.chunk_size:
                current_chunk = potential_chunk
            else:
                # 保存當前塊
                if current_chunk.strip():
                    result.append(current_chunk.strip())

                # 如果單個部分就超過大小，需要進一步切割
                if len(part_with_sep) > self.chunk_size:
                    sub_chunks = self._recursive_split(
                        part_with_sep,
                        remaining_separators
                    )
                    result.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part_with_sep

        # 處理最後一個塊
        if current_chunk.strip():
            result.append(current_chunk.strip())

        return result

    def _force_split(self, text: str) -> List[str]:
        """強制按固定大小切割"""
        result = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # 嘗試在單詞邊界切割
            if end < len(text):
                # 往回找空格
                last_space = text.rfind(" ", start, end)
                if last_space > start + self.chunk_size // 2:
                    end = last_space + 1

            chunk = text[start:end].strip()
            if chunk:
                result.append(chunk)

            start = end - self.chunk_overlap
            if start >= len(text):
                break

        return result

    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """合併過小的塊"""
        if not chunks:
            return []

        min_size = self.chunk_size // 4  # 最小塊大小為目標的 1/4
        result = []
        current = ""

        for chunk in chunks:
            if len(chunk) < min_size and current:
                # 嘗試合併到前一個塊
                if len(current) + len(chunk) <= self.chunk_size:
                    current = current + " " + chunk
                    continue

            if current:
                result.append(current)
            current = chunk

        if current:
            result.append(current)

        return result


# 單例實例
chunker = TextChunker()
