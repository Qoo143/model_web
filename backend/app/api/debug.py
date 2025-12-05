"""
調試 API 路由

提供系統狀態查詢功能
"""

from fastapi import APIRouter, Depends
from typing import Any

from app.api.deps import get_current_user
from app.models.user import User
from app.services.rag.vectorstore import vectorstore_service
from app.services.rag.embedder import embedding_service
from app.core.config import settings


router = APIRouter(
    prefix="/debug",
    tags=["Debug"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/chroma-status",
    summary="取得 Chroma 向量庫狀態",
    description="查看向量資料庫的狀態資訊，包含向量數量等（無需認證）"
)
async def get_chroma_status() -> Any:
    """取得 Chroma 向量庫狀態（公開端點，用於調試）"""
    
    try:
        # 確保 collection 存在
        collection_id = await vectorstore_service._ensure_collection()
        
        # 取得向量數量
        count = await vectorstore_service.count()
        
        # 健康檢查
        is_healthy = await vectorstore_service.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "collection_name": vectorstore_service.collection_name,
            "collection_id": collection_id,
            "vector_count": count,
            "chroma_url": vectorstore_service.base_url,
            "embedding_model": embedding_service.model,
            "settings": {
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "top_k_retrieval": settings.TOP_K_RETRIEVAL
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "chroma_url": vectorstore_service.base_url
        }


@router.get(
    "/rag-config",
    summary="取得 RAG 配置",
    description="查看當前 RAG 系統的配置"
)
async def get_rag_config(
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得 RAG 配置"""
    
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_model": settings.EMBEDDING_MODEL,
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "top_k_retrieval": settings.TOP_K_RETRIEVAL,
        "gemini_model": settings.GEMINI_MODEL if settings.LLM_PROVIDER == "gemini" else None,
        "ollama_model": settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else None
    }
