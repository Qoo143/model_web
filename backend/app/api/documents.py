"""
文件管理 API 路由

提供文件上傳、列表、刪除等功能
僅支援 txt 和 md 格式
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.group import Group, GroupMember, GroupRole
from app.models.document import Document, DocumentStatus, DocumentRole
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentProcessingStatus,
    MessageResponse,
    UploadResponse,
)
from app.services.document.processor import DocumentProcessor

# 建立路由器
router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Not found"}},
)


# ============================================
# 輔助函數
# ============================================

def get_file_extension(filename: str) -> str:
    """取得檔案副檔名（小寫）"""
    return Path(filename).suffix.lower().lstrip(".")


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一的儲存檔名"""
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}.{ext}"


async def check_group_permission(
    db: AsyncSession,
    user_id: int,
    group_id: int,
    min_role: GroupRole = GroupRole.VIEWER
) -> GroupMember:
    """
    檢查使用者在群組中的權限

    Args:
        db: 資料庫 session
        user_id: 使用者 ID
        group_id: 群組 ID
        min_role: 最低要求的角色

    Returns:
        GroupMember: 成員資訊

    Raises:
        HTTPException: 權限不足
    """
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

    # 角色權限層級
    role_hierarchy = {
        GroupRole.OWNER: 4,
        GroupRole.ADMIN: 3,
        GroupRole.EDITOR: 2,
        GroupRole.VIEWER: 1
    }

    if role_hierarchy[member.role] < role_hierarchy[min_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要 {min_role.value} 或以上權限"
        )

    return member


def can_view_document(member_role: GroupRole, doc_min_role: DocumentRole) -> bool:
    """檢查使用者是否有權限查看文件"""
    role_hierarchy = {
        "owner": 4,
        "admin": 3,
        "editor": 2,
        "viewer": 1
    }
    return role_hierarchy[member_role.value] >= role_hierarchy[doc_min_role.value]


# ============================================
# 文件處理後台任務
# ============================================

async def process_document_task(document_id: int):
    """後台處理文件任務"""
    import logging
    from app.core.database import AsyncSessionLocal
    
    logging.info(f"Starting document processing for document_id={document_id}")
    
    processor = DocumentProcessor()
    try:
        # 創建獨立的資料庫 session
        async with AsyncSessionLocal() as db:
            result = await processor.process_document(db, document_id)
            if result.success:
                logging.info(f"Document processing completed for document_id={document_id}, chunks={result.chunk_count}")
            else:
                logging.error(f"Document processing failed for document_id={document_id}: {result.error_message}")
    except Exception as e:
        logging.error(f"Document processing failed for document_id={document_id}: {e}")


# ============================================
# 文件上傳 API
# ============================================

@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="上傳文件",
    description="""
    上傳文件到指定群組

    業務邏輯：
    1. 驗證檔案類型（僅支援 txt/md）
    2. 驗證檔案大小
    3. 驗證使用者在群組中的權限（需要 editor 以上）
    4. 儲存檔案到本地
    5. 建立文件記錄（狀態為 pending）
    6. 觸發後台處理（分塊、向量化）

    注意：
    - 使用 multipart/form-data 格式
    - 最大檔案大小由 MAX_FILE_SIZE 設定控制
    """
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="要上傳的文件"),
    group_id: int = Form(..., description="目標群組 ID"),
    min_view_role: DocumentRole = Form(
        default=DocumentRole.VIEWER,
        description="查看此文件所需的最低權限"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """上傳文件"""

    # 1. 驗證檔案類型
    file_ext = get_file_extension(file.filename)
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支援的檔案類型: {file_ext}。僅支援: {', '.join(settings.ALLOWED_FILE_TYPES)}"
        )

    # 2. 驗證檔案大小（讀取檔案內容來計算）
    content = await file.read()
    file_size = len(content)

    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"檔案大小超過限制。最大: {settings.MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能上傳空檔案"
        )

    # 3. 檢查群組是否存在
    group_result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = group_result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 4. 檢查使用者權限（需要 editor 以上）
    await check_group_permission(db, current_user.id, group_id, GroupRole.EDITOR)

    # 5. 生成唯一檔名並儲存
    unique_filename = generate_unique_filename(file.filename)
    group_storage_dir = Path(settings.UPLOAD_DIR) / str(group_id)
    group_storage_dir.mkdir(parents=True, exist_ok=True)
    file_path = group_storage_dir / unique_filename

    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"檔案儲存失敗: {str(e)}"
        )

    # 6. 建立文件記錄
    new_document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_type=file_ext,
        file_size=file_size,
        file_path=str(file_path),
        group_id=group_id,
        uploader_id=current_user.id,
        processing_status=DocumentStatus.PENDING,
        min_view_role=min_view_role,
        chunk_count=0,
        page_count=0
    )
    db.add(new_document)

    # 7. 更新群組文件數
    group.document_count += 1

    await db.commit()
    await db.refresh(new_document)

    # 8. 觸發後台處理
    background_tasks.add_task(process_document_task, new_document.id)

    return UploadResponse(
        message="文件上傳成功，正在處理中",
        document=DocumentResponse(
            id=new_document.id,
            filename=new_document.filename,
            original_filename=new_document.original_filename,
            file_type=new_document.file_type,
            file_size=new_document.file_size,
            group_id=new_document.group_id,
            uploader_id=new_document.uploader_id,
            uploader_username=current_user.username,
            processing_status=new_document.processing_status,
            error_message=new_document.error_message,
            chunk_count=new_document.chunk_count,
            page_count=new_document.page_count,
            min_view_role=new_document.min_view_role,
            created_at=new_document.created_at,
            updated_at=new_document.updated_at
        )
    )


# ============================================
# 文件列表 API
# ============================================

@router.get(
    "",
    response_model=DocumentListResponse,
    summary="取得文件列表",
    description="""
    取得群組中的文件列表

    業務邏輯：
    - 需要指定群組 ID
    - 只返回使用者有權限查看的文件
    - 支援分頁和篩選
    """
)
async def list_documents(
    group_id: int = Query(..., description="群組 ID"),
    skip: int = Query(0, ge=0, description="跳過筆數"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    status_filter: Optional[DocumentStatus] = Query(None, description="狀態篩選"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得文件列表"""

    # 1. 檢查使用者權限
    member = await check_group_permission(db, current_user.id, group_id)

    # 2. 根據使用者角色篩選可查看的文件
    role_hierarchy = {
        GroupRole.OWNER: ["owner", "admin", "editor", "viewer"],
        GroupRole.ADMIN: ["admin", "editor", "viewer"],
        GroupRole.EDITOR: ["editor", "viewer"],
        GroupRole.VIEWER: ["viewer"]
    }
    accessible_roles = role_hierarchy[member.role]

    # 3. 建立查詢
    query = (
        select(Document)
        .options(selectinload(Document.uploader))
        .where(
            and_(
                Document.group_id == group_id,
                Document.min_view_role.in_(accessible_roles)
            )
        )
    )

    # 4. 套用狀態篩選
    if status_filter:
        query = query.where(Document.processing_status == status_filter)

    # 5. 執行查詢
    result = await db.execute(
        query.order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()

    # 6. 計算總數
    count_query = (
        select(func.count(Document.id))
        .where(
            and_(
                Document.group_id == group_id,
                Document.min_view_role.in_(accessible_roles)
            )
        )
    )
    if status_filter:
        count_query = count_query.where(Document.processing_status == status_filter)

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # 7. 構建回應
    documents_response = [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            group_id=doc.group_id,
            uploader_id=doc.uploader_id,
            uploader_username=doc.uploader.username if doc.uploader else None,
            processing_status=doc.processing_status,
            error_message=doc.error_message,
            chunk_count=doc.chunk_count,
            page_count=doc.page_count,
            min_view_role=doc.min_view_role,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
        for doc in documents
    ]

    return DocumentListResponse(total=total, documents=documents_response)


# ============================================
# 取得文件詳情 API
# ============================================

@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="取得文件詳情",
    description="取得文件的詳細資訊"
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得文件詳情"""

    # 1. 查詢文件
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.uploader))
        .options(selectinload(Document.group))
        .where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 2. 檢查使用者群組權限
    member = await check_group_permission(db, current_user.id, document.group_id)

    # 3. 檢查文件檢視權限
    if not can_view_document(member.role, document.min_view_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限查看此文件"
        )

    return DocumentDetailResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_type=document.file_type,
        file_size=document.file_size,
        group_id=document.group_id,
        uploader_id=document.uploader_id,
        uploader_username=document.uploader.username if document.uploader else None,
        processing_status=document.processing_status,
        error_message=document.error_message,
        chunk_count=document.chunk_count,
        page_count=document.page_count,
        min_view_role=document.min_view_role,
        created_at=document.created_at,
        updated_at=document.updated_at,
        group_name=document.group.name if document.group else ""
    )


# ============================================
# 下載文件 API
# ============================================

@router.get(
    "/{document_id}/download",
    summary="下載文件",
    description="下載原始文件"
)
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> FileResponse:
    """下載文件"""

    # 1. 查詢文件
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 2. 檢查使用者群組權限
    member = await check_group_permission(db, current_user.id, document.group_id)

    # 3. 檢查文件檢視權限
    if not can_view_document(member.role, document.min_view_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限下載此文件"
        )

    # 4. 檢查檔案是否存在
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="檔案不存在"
        )

    # 5. 返回檔案
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
        media_type="application/octet-stream"
    )


# ============================================
# 更新文件 API
# ============================================

@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="更新文件",
    description="""
    更新文件設定

    業務邏輯：
    - 只有上傳者、群組 owner 或 admin 可以更新
    - 目前只能更新查看權限
    """
)
async def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新文件"""

    # 1. 查詢文件
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.uploader))
        .where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 2. 檢查使用者權限
    member = await check_group_permission(db, current_user.id, document.group_id)

    # 只有上傳者、owner 或 admin 可以更新
    is_uploader = document.uploader_id == current_user.id
    is_admin_or_owner = member.role in [GroupRole.OWNER, GroupRole.ADMIN]

    if not is_uploader and not is_admin_or_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有上傳者或管理員可以更新文件"
        )

    # 3. 更新文件
    if update_data.min_view_role is not None:
        document.min_view_role = update_data.min_view_role

    await db.commit()
    await db.refresh(document)

    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_type=document.file_type,
        file_size=document.file_size,
        group_id=document.group_id,
        uploader_id=document.uploader_id,
        uploader_username=document.uploader.username if document.uploader else None,
        processing_status=document.processing_status,
        error_message=document.error_message,
        chunk_count=document.chunk_count,
        page_count=document.page_count,
        min_view_role=document.min_view_role,
        created_at=document.created_at,
        updated_at=document.updated_at
    )


# ============================================
# 刪除文件 API
# ============================================

@router.delete(
    "/{document_id}",
    response_model=MessageResponse,
    summary="刪除文件",
    description="""
    刪除文件

    業務邏輯：
    - 只有上傳者、群組 owner 或 admin 可以刪除
    - 會同時刪除本地檔案和向量庫資料
    """
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """刪除文件"""

    # 1. 查詢文件
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.group))
        .where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 2. 檢查使用者權限
    member = await check_group_permission(db, current_user.id, document.group_id)

    # 只有上傳者、owner 或 admin 可以刪除
    is_uploader = document.uploader_id == current_user.id
    is_admin_or_owner = member.role in [GroupRole.OWNER, GroupRole.ADMIN]

    if not is_uploader and not is_admin_or_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有上傳者或管理員可以刪除文件"
        )

    # 3. 刪除本地檔案
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            # 記錄錯誤但繼續刪除資料庫記錄
            print(f"刪除檔案失敗: {e}")

    # TODO: 刪除向量庫資料（Phase 3 實作）
    # await vectorstore.delete_document(document_id)

    # 4. 更新群組文件數
    if document.group:
        document.group.document_count -= 1

    # 5. 刪除資料庫記錄
    original_filename = document.original_filename
    await db.delete(document)
    await db.commit()

    return MessageResponse(
        message="文件已刪除",
        detail=f"文件 '{original_filename}' 已成功刪除"
    )


# ============================================
# 取得文件處理狀態 API
# ============================================

@router.get(
    "/{document_id}/status",
    response_model=DocumentProcessingStatus,
    summary="取得文件處理狀態",
    description="取得文件的處理狀態和進度"
)
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得文件處理狀態"""

    # 1. 查詢文件
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 2. 檢查使用者權限
    await check_group_permission(db, current_user.id, document.group_id)

    # 3. 計算進度（根據狀態）
    progress_map = {
        DocumentStatus.PENDING: 0,
        DocumentStatus.PROCESSING: 50,
        DocumentStatus.COMPLETED: 100,
        DocumentStatus.FAILED: 0
    }

    return DocumentProcessingStatus(
        document_id=document.id,
        status=document.processing_status,
        progress=progress_map.get(document.processing_status, 0),
        error_message=document.error_message,
        chunk_count=document.chunk_count if document.processing_status == DocumentStatus.COMPLETED else None
    )
