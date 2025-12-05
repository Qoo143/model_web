"""
文件解析器

負責解析 TXT 和 Markdown 文件，提取純文字內容
"""

import os
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ParsedDocument:
    """解析後的文件資料"""
    content: str
    title: Optional[str] = None
    word_count: int = 0
    line_count: int = 0
    file_type: str = ""


class DocumentParser:
    """
    文件解析器

    支援的格式：
    - TXT: 純文字檔案（UTF-8）
    - MD: Markdown 檔案（保留結構標記）

    業務邏輯：
    - 讀取檔案內容
    - 處理編碼問題
    - 提取標題（如果有）
    - 計算統計資訊
    """

    SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "gbk", "big5", "latin-1"]

    def __init__(self):
        pass

    def parse(self, file_path: str) -> ParsedDocument:
        """
        解析文件

        Args:
            file_path: 文件路徑

        Returns:
            ParsedDocument: 解析結果

        Raises:
            FileNotFoundError: 檔案不存在
            ValueError: 不支援的檔案格式
            UnicodeDecodeError: 編碼錯誤
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"檔案不存在: {file_path}")

        # 取得檔案類型
        file_ext = path.suffix.lower().lstrip(".")
        if file_ext not in ["txt", "md"]:
            raise ValueError(f"不支援的檔案格式: {file_ext}")

        # 讀取檔案內容（嘗試多種編碼）
        content = self._read_file_with_encoding(file_path)

        # 解析內容
        if file_ext == "md":
            return self._parse_markdown(content, file_ext)
        else:
            return self._parse_text(content, file_ext)

    def _read_file_with_encoding(self, file_path: str) -> str:
        """
        嘗試使用多種編碼讀取檔案

        Args:
            file_path: 檔案路徑

        Returns:
            str: 檔案內容
        """
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # 如果所有編碼都失敗，使用 errors='replace' 強制讀取
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _parse_text(self, content: str, file_type: str) -> ParsedDocument:
        """解析純文字檔案"""
        # 清理內容
        content = content.strip()

        # 計算統計
        lines = content.split("\n")
        line_count = len(lines)
        word_count = len(content)

        # 嘗試提取標題（第一行非空行）
        title = None
        for line in lines:
            line = line.strip()
            if line:
                title = line[:100]  # 限制標題長度
                break

        return ParsedDocument(
            content=content,
            title=title,
            word_count=word_count,
            line_count=line_count,
            file_type=file_type
        )

    def _parse_markdown(self, content: str, file_type: str) -> ParsedDocument:
        """
        解析 Markdown 檔案

        保留 Markdown 結構以便後續處理
        但移除純格式標記
        """
        content = content.strip()

        # 計算統計
        lines = content.split("\n")
        line_count = len(lines)
        word_count = len(content)

        # 嘗試提取 H1 標題
        title = None
        for line in lines:
            line_stripped = line.strip()
            # 匹配 # 開頭的標題
            if line_stripped.startswith("# "):
                title = line_stripped[2:].strip()[:100]
                break
            # 跳過空行和元數據
            if line_stripped and not line_stripped.startswith("---"):
                # 如果沒有 H1，使用第一行非空內容
                if title is None:
                    title = line_stripped[:100]
                break

        # 移除 YAML frontmatter（如果有）
        content = self._remove_frontmatter(content)

        return ParsedDocument(
            content=content,
            title=title,
            word_count=word_count,
            line_count=line_count,
            file_type=file_type
        )

    def _remove_frontmatter(self, content: str) -> str:
        """移除 YAML frontmatter"""
        if content.startswith("---"):
            # 找到結束的 ---
            end_index = content.find("---", 3)
            if end_index != -1:
                content = content[end_index + 3:].strip()
        return content

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """取得檔案類型"""
        return Path(file_path).suffix.lower().lstrip(".")


# 單例實例
parser = DocumentParser()
