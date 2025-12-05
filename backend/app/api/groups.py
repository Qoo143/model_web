"""
群組管理 API 路由

提供群組 CRUD 和成員管理功能
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember, GroupRole
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupDetailResponse,
    GroupListResponse,
    GroupMemberAdd,
    GroupMemberUpdate,
    GroupMemberResponse,
    MessageResponse,
)

# 建立路由器
router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)


# ============================================
# 群組 CRUD API
# ============================================

@router.post(
    "",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="建立群組",
    description="""
    建立新群組

    業務邏輯：
    1. 當前使用者成為群組擁有者
    2. 自動新增使用者為群組成員（角色為 owner）
    3. 預設為私有群組
    """
)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """建立新群組"""

    # 1. 建立群組
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        is_private=group_data.is_private,
        owner_id=current_user.id,
        member_count=1,
        document_count=0
    )
    db.add(new_group)
    await db.flush()  # 取得 new_group.id

    # 2. 新增擁有者為群組成員
    owner_member = GroupMember(
        group_id=new_group.id,
        user_id=current_user.id,
        role=GroupRole.OWNER,
        is_active=True
    )
    db.add(owner_member)
    await db.commit()
    await db.refresh(new_group)

    return new_group


@router.get(
    "",
    response_model=GroupListResponse,
    summary="取得群組列表",
    description="""
    取得當前使用者加入的所有群組

    業務邏輯：
    - 只返回使用者是成員的群組
    - 支援分頁
    """
)
async def list_groups(
    skip: int = Query(0, ge=0, description="跳過筆數"),
    limit: int = Query(20, ge=1, le=100, description="每頁筆數"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得使用者的群組列表"""

    # 查詢使用者加入的群組
    result = await db.execute(
        select(Group)
        .join(GroupMember, Group.id == GroupMember.group_id)
        .where(
            and_(
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
        .order_by(Group.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    groups = result.scalars().all()

    # 計算總數
    count_result = await db.execute(
        select(func.count(Group.id))
        .join(GroupMember, Group.id == GroupMember.group_id)
        .where(
            and_(
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
    )
    total = count_result.scalar()

    return GroupListResponse(total=total, groups=groups)


@router.get(
    "/{group_id}",
    response_model=GroupDetailResponse,
    summary="取得群組詳情",
    description="""
    取得群組詳細資訊

    業務邏輯：
    - 只有群組成員可以查看
    - 包含成員列表和當前使用者角色
    """
)
async def get_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得群組詳情"""

    # 1. 查詢群組（包含成員）
    result = await db.execute(
        select(Group)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
        .options(selectinload(Group.owner))
        .where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 2. 檢查使用者是否為成員
    member = next(
        (m for m in group.members if m.user_id == current_user.id and m.is_active),
        None
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是此群組的成員"
        )

    # 3. 構建回應
    members_response = [
        GroupMemberResponse(
            id=m.id,
            user_id=m.user_id,
            username=m.user.username,
            email=m.user.email,
            full_name=m.user.full_name,
            role=m.role,
            joined_at=m.joined_at,
            is_active=m.is_active
        )
        for m in group.members if m.is_active
    ]

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        is_private=group.is_private,
        owner_id=group.owner_id,
        owner_username=group.owner.username,
        member_count=group.member_count,
        document_count=group.document_count,
        created_at=group.created_at,
        updated_at=group.updated_at,
        current_user_role=member.role,
        members=members_response
    )


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="更新群組",
    description="""
    更新群組資訊

    業務邏輯：
    - 只有 owner 和 admin 可以更新
    """
)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新群組"""

    # 1. 查詢群組
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 2. 檢查權限
    member_result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
    )
    member = member_result.scalar_one_or_none()

    if not member or member.role not in [GroupRole.OWNER, GroupRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有擁有者或管理員可以更新群組"
        )

    # 3. 更新群組
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    if group_data.is_private is not None:
        group.is_private = group_data.is_private

    await db.commit()
    await db.refresh(group)

    return group


@router.delete(
    "/{group_id}",
    response_model=MessageResponse,
    summary="刪除群組",
    description="""
    刪除群組

    業務邏輯：
    - 只有 owner 可以刪除群組
    - 會同時刪除所有成員記錄、文件和對話
    """
)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """刪除群組"""

    # 1. 查詢群組
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 2. 檢查權限（只有擁有者可以刪除）
    if group.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有群組擁有者可以刪除群組"
        )

    # 3. 刪除群組（cascade 會自動刪除相關記錄）
    await db.delete(group)
    await db.commit()

    return MessageResponse(
        message="群組已刪除",
        detail=f"群組 '{group.name}' 已成功刪除"
    )


# ============================================
# 群組成員管理 API
# ============================================

@router.post(
    "/{group_id}/members",
    response_model=GroupMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新增群組成員",
    description="""
    新增成員到群組

    業務邏輯：
    - 只有 owner 和 admin 可以新增成員
    - admin 不能新增 owner 或 admin
    - 使用者不能重複加入同一群組
    """
)
async def add_member(
    group_id: int,
    member_data: GroupMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """新增群組成員"""

    # 1. 查詢群組
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 2. 檢查當前使用者權限
    current_member_result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
    )
    current_member = current_member_result.scalar_one_or_none()

    if not current_member or current_member.role not in [GroupRole.OWNER, GroupRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有擁有者或管理員可以新增成員"
        )

    # 3. admin 不能新增 owner 或 admin
    if current_member.role == GroupRole.ADMIN and member_data.role in [GroupRole.OWNER, GroupRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理員不能新增擁有者或管理員角色"
        )

    # 4. 檢查目標使用者是否存在
    user_result = await db.execute(
        select(User).where(User.id == member_data.user_id)
    )
    target_user = user_result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="使用者不存在"
        )

    # 5. 檢查是否已經是成員
    existing_member_result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == member_data.user_id
            )
        )
    )
    existing_member = existing_member_result.scalar_one_or_none()

    if existing_member:
        if existing_member.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="使用者已經是群組成員"
            )
        else:
            # 重新啟用成員
            existing_member.is_active = True
            existing_member.role = member_data.role
            await db.commit()
            await db.refresh(existing_member)

            return GroupMemberResponse(
                id=existing_member.id,
                user_id=target_user.id,
                username=target_user.username,
                email=target_user.email,
                full_name=target_user.full_name,
                role=existing_member.role,
                joined_at=existing_member.joined_at,
                is_active=existing_member.is_active
            )

    # 6. 新增成員
    new_member = GroupMember(
        group_id=group_id,
        user_id=member_data.user_id,
        role=member_data.role,
        is_active=True
    )
    db.add(new_member)

    # 7. 更新群組成員數
    group.member_count += 1

    await db.commit()
    await db.refresh(new_member)

    return GroupMemberResponse(
        id=new_member.id,
        user_id=target_user.id,
        username=target_user.username,
        email=target_user.email,
        full_name=target_user.full_name,
        role=new_member.role,
        joined_at=new_member.joined_at,
        is_active=new_member.is_active
    )


@router.put(
    "/{group_id}/members/{user_id}",
    response_model=GroupMemberResponse,
    summary="更新成員角色",
    description="""
    更新群組成員的角色

    業務邏輯：
    - 只有 owner 可以更新任何成員的角色
    - admin 只能更新 editor 和 viewer 的角色
    - 不能更新擁有者的角色
    """
)
async def update_member_role(
    group_id: int,
    user_id: int,
    update_data: GroupMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """更新成員角色"""

    # 1. 查詢群組
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 2. 檢查當前使用者權限
    current_member_result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
    )
    current_member = current_member_result.scalar_one_or_none()

    if not current_member or current_member.role not in [GroupRole.OWNER, GroupRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有擁有者或管理員可以更新成員角色"
        )

    # 3. 查詢目標成員
    target_member_result = await db.execute(
        select(GroupMember)
        .options(selectinload(GroupMember.user))
        .where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.is_active == True
            )
        )
    )
    target_member = target_member_result.scalar_one_or_none()

    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成員不存在"
        )

    # 4. 不能更新擁有者角色
    if target_member.role == GroupRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能更新擁有者的角色"
        )

    # 5. admin 不能設定 owner 或 admin 角色
    if current_member.role == GroupRole.ADMIN:
        if target_member.role == GroupRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理員不能更新其他管理員的角色"
            )
        if update_data.role in [GroupRole.OWNER, GroupRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理員不能設定擁有者或管理員角色"
            )

    # 6. 更新角色
    target_member.role = update_data.role
    await db.commit()
    await db.refresh(target_member)

    return GroupMemberResponse(
        id=target_member.id,
        user_id=target_member.user_id,
        username=target_member.user.username,
        email=target_member.user.email,
        full_name=target_member.user.full_name,
        role=target_member.role,
        joined_at=target_member.joined_at,
        is_active=target_member.is_active
    )


@router.delete(
    "/{group_id}/members/{user_id}",
    response_model=MessageResponse,
    summary="移除群組成員",
    description="""
    從群組移除成員

    業務邏輯：
    - 擁有者可以移除任何成員（除了自己）
    - 管理員可以移除 editor 和 viewer
    - 成員可以自己離開群組
    - 擁有者不能離開群組（需先轉移所有權）
    """
)
async def remove_member(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """移除群組成員"""

    # 1. 查詢群組
    result = await db.execute(
        select(Group).where(Group.id == group_id)
    )
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="群組不存在"
        )

    # 2. 查詢當前使用者的成員資格
    current_member_result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
    )
    current_member = current_member_result.scalar_one_or_none()

    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是此群組的成員"
        )

    # 3. 查詢目標成員
    target_member_result = await db.execute(
        select(GroupMember)
        .options(selectinload(GroupMember.user))
        .where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id,
                GroupMember.is_active == True
            )
        )
    )
    target_member = target_member_result.scalar_one_or_none()

    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成員不存在"
        )

    # 4. 擁有者不能離開群組
    if target_member.role == GroupRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="擁有者不能離開群組，請先轉移所有權"
        )

    # 5. 檢查權限
    is_self_leave = user_id == current_user.id
    is_owner = current_member.role == GroupRole.OWNER
    is_admin = current_member.role == GroupRole.ADMIN
    target_is_admin = target_member.role == GroupRole.ADMIN

    if not is_self_leave:
        if not is_owner and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有擁有者或管理員可以移除其他成員"
            )
        if is_admin and target_is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理員不能移除其他管理員"
            )

    # 6. 標記成員為非活躍（軟刪除）
    target_member.is_active = False

    # 7. 更新群組成員數
    group.member_count -= 1

    await db.commit()

    username = target_member.user.username
    if is_self_leave:
        return MessageResponse(
            message="已離開群組",
            detail=f"您已離開群組 '{group.name}'"
        )
    else:
        return MessageResponse(
            message="成員已移除",
            detail=f"已將 {username} 從群組 '{group.name}' 移除"
        )


@router.get(
    "/{group_id}/members",
    response_model=List[GroupMemberResponse],
    summary="取得群組成員列表",
    description="取得群組的所有成員"
)
async def list_members(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """取得群組成員列表"""

    # 1. 檢查使用者是否為成員
    current_member_result = await db.execute(
        select(GroupMember).where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.user_id == current_user.id,
                GroupMember.is_active == True
            )
        )
    )
    current_member = current_member_result.scalar_one_or_none()

    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是此群組的成員"
        )

    # 2. 查詢所有成員
    result = await db.execute(
        select(GroupMember)
        .options(selectinload(GroupMember.user))
        .where(
            and_(
                GroupMember.group_id == group_id,
                GroupMember.is_active == True
            )
        )
        .order_by(GroupMember.role, GroupMember.joined_at)
    )
    members = result.scalars().all()

    return [
        GroupMemberResponse(
            id=m.id,
            user_id=m.user_id,
            username=m.user.username,
            email=m.user.email,
            full_name=m.user.full_name,
            role=m.role,
            joined_at=m.joined_at,
            is_active=m.is_active
        )
        for m in members
    ]
