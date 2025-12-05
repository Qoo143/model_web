"""
對話 Schema

定義對話和訊息的 API 請求和回應格式
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.message import MessageRole


# ============================================
# 訊息 Schema
# ============================================
class MessageBase(BaseModel):
    """訊息基礎 Schema"""
    content: str = Field(..., min_length=1, max_length=10000, description="訊息內容")


class MessageCreate(MessageBase):
    """建立訊息（發送問題）"""
    document_ids: Optional[List[int]] = Field(
        None,
        description="限制在這些文件中搜尋（可選）"
    )
    llm_provider: Optional[str] = Field(
        None,
        description="LLM 提供者：ollama 或 gemini（可選）"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "這份文件的主要內容是什麼？",
                "document_ids": [1, 2],
                "llm_provider": "ollama"
            }
        }
    )


class SourceReference(BaseModel):
    """來源引用"""
    document_id: int
    document_name: str
    chunk_index: Optional[int] = None
    content: str
    score: float


class MessageResponse(BaseModel):
    """訊息回應 Schema"""
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    sources: Optional[List[SourceReference]] = None
    token_count: Optional[int] = None
    generation_time: Optional[float] = None
    model_used: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ============================================
# 對話 Schema
# ============================================
class ConversationBase(BaseModel):
    """對話基礎 Schema"""
    title: Optional[str] = Field(None, max_length=200, description="對話標題")


class ConversationCreate(ConversationBase):
    """建立對話"""
    group_id: int = Field(..., description="群組 ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "group_id": 1,
                "title": "關於年度報告的討論"
            }
        }
    )


class ConversationUpdate(BaseModel):
    """更新對話"""
    title: Optional[str] = Field(None, max_length=200)


class ConversationResponse(BaseModel):
    """對話回應 Schema"""
    id: int
    user_id: int
    group_id: int
    group_name: Optional[str] = None
    title: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(ConversationResponse):
    """對話詳情回應（包含訊息）"""
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """對話列表回應"""
    total: int
    conversations: List[ConversationResponse]


# ============================================
# 問答 Schema
# ============================================
class ChatRequest(BaseModel):
    """問答請求"""
    question: str = Field(..., min_length=1, max_length=10000, description="問題")
    conversation_id: Optional[int] = Field(None, description="對話 ID（可選，為空則建立新對話）")
    group_id: int = Field(..., description="群組 ID")
    document_ids: Optional[List[int]] = Field(None, description="限制在這些文件中搜尋")
    llm_provider: Optional[str] = Field(None, description="LLM 提供者")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "這份文件的主要內容是什麼？",
                "group_id": 1,
                "document_ids": [1, 2],
                "llm_provider": "ollama"
            }
        }
    )


class ChatResponse(BaseModel):
    """問答回應"""
    conversation_id: int
    message_id: int
    answer: str
    sources: List[SourceReference]
    model: str
    confidence: float
    generation_time: Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": 1,
                "message_id": 1,
                "answer": "根據文件內容，主要內容是...",
                "sources": [
                    {
                        "document_id": 1,
                        "document_name": "report.txt",
                        "content": "相關內容片段...",
                        "score": 0.89
                    }
                ],
                "model": "gpt-oss-20b",
                "confidence": 0.85,
                "generation_time": 2.5
            }
        }
    )


# ============================================
# 通用回應
# ============================================
class MessageResponseSimple(BaseModel):
    """通用訊息回應"""
    message: str
    detail: Optional[str] = None
