"""
對話管理 API 路由

提供對話 CRUD 和問答功能
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
import json

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember, GroupRole
from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.schemas.chat import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    SourceReference,
    ChatRequest,
    ChatResponse,
    MessageResponseSimple,
)
from app.services.rag.chain import rag_chain

# 建立路由器
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)


# ============================================
# 輔助函數
# ============================================

async def check_group_access(
    db: AsyncSession,
    user_id: int,
    group_id: int
) -> GroupMember:
    """檢查使用者是否有權限訪問群組"""
    result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.is_active == True
            )
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是此群組的成員"
        )

    return member


# ============================================
# 對話 CRUD API
# ============================================

@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="建立對話",
    description="在指定群組中建立新對話"
)
async def create_conversation(
    data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """建立新對話"""

    # 1. 檢查群組存取權限
    await check_group_access(db, current_user.id, data.group_id)

    # 2. 取得群組資訊
    group_result = await db.execute(
        select(Group).where(Group.id == data.group_id)
    )
    group = group_result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 3. 建立對話
    new_conversation = Conversation(
        user_id=current_user.id,
        group_id=data.group_id,
        title=data.title or "新對話",
        message_count=0
    )
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)

    return ConversationResponse(
        id=new_conversation.id,
        user_id=new_conversation.user_id,
        group_id=new_conversation.group_id,
        group_name=group.name,
        title=new_conversation.title,
        message_count=new_conversation.message_count,
        created_at=new_conversation.created_at,
        updated_at=new_conversation.updated_at
    )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="取得對話列表",
    description="取得使用者的對話列表"
)
async def list_conversations(
    group_id: Optional[int] = Query(None, description="篩選群組"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得對話列表"""

    # 建立查詢
    query = (
        select(Conversation)
        .options(selectinload(Conversation.group))
        .where(Conversation.user_id == current_user.id)
    )

    if group_id:
        query = query.where(Conversation.group_id == group_id)

    # 執行查詢
    result = await db.execute(
        query.order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    conversations = result.scalars().all()

    # 計算總數
    count_query = select(func.count(Conversation.id)).where(
        Conversation.user_id == current_user.id
    )
    if group_id:
        count_query = count_query.where(Conversation.group_id == group_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return ConversationListResponse(
        total=total,
        conversations=[
            ConversationResponse(
                id=c.id,
                user_id=c.user_id,
                group_id=c.group_id,
                group_name=c.group.name if c.group else None,
                title=c.title,
                message_count=c.message_count,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in conversations
        ]
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="取得對話詳情",
    description="取得對話詳情包含訊息歷史"
)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得對話詳情"""

    # 查詢對話
    result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.group),
            selectinload(Conversation.messages)
        )
        .where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="對話不存在"
        )

    # 轉換訊息
    messages = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            sources=[
                SourceReference(**s) for s in m.sources
            ] if m.sources else None,
            token_count=m.token_count,
            generation_time=m.generation_time,
            model_used=m.model_used,
            created_at=m.created_at
        )
        for m in sorted(conversation.messages, key=lambda x: x.created_at)
    ]

    return ConversationDetailResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        group_id=conversation.group_id,
        group_name=conversation.group.name if conversation.group else None,
        title=conversation.title,
        message_count=conversation.message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages
    )


@router.put(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    summary="更新對話",
    description="更新對話標題"
)
async def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新對話"""

    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.group))
        .where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="對話不存在"
        )

    if data.title is not None:
        conversation.title = data.title

    await db.commit()
    await db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        group_id=conversation.group_id,
        group_name=conversation.group.name if conversation.group else None,
        title=conversation.title,
        message_count=conversation.message_count,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.delete(
    "/conversations/{conversation_id}",
    response_model=MessageResponseSimple,
    summary="刪除對話",
    description="刪除對話及其所有訊息"
)
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """刪除對話"""

    result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="對話不存在"
        )

    title = conversation.title
    await db.delete(conversation)
    await db.commit()

    return MessageResponseSimple(
        message="對話已刪除",
        detail=f"對話 '{title}' 已成功刪除"
    )


# ============================================
# 問答 API
# ============================================

@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="問答",
    description="""
    向 RAG 系統提問

    業務邏輯：
    1. 驗證群組存取權限
    2. 建立或使用現有對話
    3. 檢索相關文件
    4. 呼叫 LLM 生成答案
    5. 儲存問答記錄
    6. 返回答案和來源
    """
)
async def ask_question(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """問答"""

    # 1. 檢查群組存取權限
    await check_group_access(db, current_user.id, request.group_id)

    # 2. 取得或建立對話
    if request.conversation_id:
        # 使用現有對話
        conv_result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                and_(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id
                )
            )
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="對話不存在"
            )
    else:
        # 建立新對話
        conversation = Conversation(
            user_id=current_user.id,
            group_id=request.group_id,
            title=request.question[:50] + "..." if len(request.question) > 50 else request.question,
            message_count=0
        )
        db.add(conversation)
        await db.flush()

    # 3. 建立使用者訊息
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=request.question
    )
    db.add(user_message)
    conversation.message_count += 1

    # 4. 取得對話歷史（最近 6 條訊息）
    conversation_history = []
    if hasattr(conversation, 'messages') and conversation.messages:
        for msg in sorted(conversation.messages, key=lambda x: x.created_at)[-6:]:
            conversation_history.append({
                "role": msg.role.value,
                "content": msg.content
            })

    # 5. 呼叫 RAG Chain
    try:
        rag_response = await rag_chain.query(
            question=request.question,
            group_id=request.group_id,
            document_ids=request.document_ids,
            conversation_history=conversation_history,
            llm_provider=request.llm_provider
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG 查詢失敗: {str(e)}"
        )

    # 6. 建立助手訊息
    sources_data = [
        {
            "document_id": s["document_id"],
            "document_name": s["document_name"],
            "chunk_index": s.get("chunk_index"),
            "content": s["content"],
            "score": s["score"]
        }
        for s in rag_response.sources
    ]

    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=rag_response.answer,
        sources=sources_data,
        token_count=rag_response.metadata.get("total_tokens"),
        generation_time=rag_response.generation_time,
        model_used=rag_response.model
    )
    db.add(assistant_message)
    conversation.message_count += 1

    await db.commit()
    await db.refresh(assistant_message)

    # 7. 返回結果
    return ChatResponse(
        conversation_id=conversation.id,
        message_id=assistant_message.id,
        answer=rag_response.answer,
        sources=[
            SourceReference(
                document_id=s["document_id"],
                document_name=s["document_name"],
                chunk_index=s.get("chunk_index"),
                content=s["content"],
                score=s["score"]
            )
            for s in sources_data
        ],
        model=rag_response.model,
        confidence=rag_response.confidence,
        generation_time=rag_response.generation_time
    )


@router.get(
    "/providers",
    summary="取得可用的 LLM 提供者",
    description="取得系統支援的 LLM 提供者列表"
)
async def get_llm_providers(
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得 LLM 提供者列表"""
    from app.services.llm.factory import LLMFactory

    return {
        "providers": LLMFactory.get_available_providers(),
        "default": "ollama"
    }
