import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.core.rate_limit import rate_limit
from app.models.pack_category import PackCategory, PackCategoryAssignment
from app.models.user import User, UserRole, UserStatus
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.registry import CategoryResponse, CreateCategoryRequest, UpdateCategoryRequest
from app.schemas.user import AdminUpdateRoleRequest, AdminUserResponse

log = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=ListResponse[AdminUserResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN)), Depends(rate_limit(10, 60))],
)
async def list_users(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page

    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar_one()

    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(offset).limit(per_page)
    )
    users = result.scalars().all()

    return ListResponse(
        data=[AdminUserResponse.model_validate(u) for u in users],
        meta=PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            has_more=(offset + per_page) < total,
        ),
    )


@router.get(
    "/users/{user_id}",
    response_model=DataResponse[AdminUserResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN)), Depends(rate_limit(10, 60))],
)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return DataResponse(data=AdminUserResponse.model_validate(user))


@router.put(
    "/users/{user_id}/role",
    response_model=DataResponse[AdminUserResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def update_user_role(
    user_id: str,
    body: AdminUpdateRoleRequest,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        new_role = UserRole(body.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid role: {body.role}") from exc

    old_role = user.role

    # Prevent removing the last active admin — demoting the final admin would
    # lock the platform out of all admin operations.
    if old_role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        admin_count = await db.execute(
            select(func.count(User.id)).where(
                User.role == UserRole.ADMIN,
                User.status == UserStatus.ACTIVE,
            )
        )
        if admin_count.scalar_one() <= 1:
            raise HTTPException(status_code=422, detail="Cannot demote the last admin")

    user.role = new_role
    await db.commit()
    await db.refresh(user)

    log.info(
        "auth_role_changed",
        user_id=user.id,
        old=old_role.value,
        new=new_role.value,
        by=admin.id,
    )

    return DataResponse(data=AdminUserResponse.model_validate(user))


@router.delete(
    "/users/{user_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def soft_delete_user(
    user_id: str,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin.id:
        raise HTTPException(status_code=422, detail="Cannot delete yourself")

    # Don't delete the last active admin (platform lockout)
    if user.role == UserRole.ADMIN:
        admin_count = await db.execute(
            select(func.count(User.id)).where(
                User.role == UserRole.ADMIN,
                User.status == UserStatus.ACTIVE,
            )
        )
        if admin_count.scalar_one() <= 1:
            raise HTTPException(status_code=422, detail="Cannot delete the last admin")

    user.status = UserStatus.DELETED
    await db.commit()


# ── Pack Category Admin CRUD ───────────────────────────


@router.post(
    "/pack-categories",
    response_model=DataResponse[CategoryResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_pack_category(
    body: CreateCategoryRequest,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new pack category (admin only)."""
    # Validate parent exists if provided
    if body.parent_id:
        parent = await db.get(PackCategory, body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")

    category = PackCategory(
        name=body.name,
        slug=body.slug,
        parent_id=body.parent_id,
        icon=body.icon,
        sort_order=body.sort_order,
    )
    db.add(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Category with this slug already exists") from None
    await db.refresh(category)

    log.info("pack_category_created", category_id=category.id, by=admin.id)
    return DataResponse(data=CategoryResponse.model_validate(category))


@router.put(
    "/pack-categories/{category_id}",
    response_model=DataResponse[CategoryResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def update_pack_category(
    category_id: str,
    body: UpdateCategoryRequest,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing pack category (admin only)."""
    category = await db.get(PackCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Validate parent if being changed
    if body.parent_id is not None:
        if body.parent_id == category_id:
            raise HTTPException(status_code=422, detail="Category cannot be its own parent")
        parent = await db.get(PackCategory, body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Category with this slug already exists") from None
    await db.refresh(category)

    log.info("pack_category_updated", category_id=category_id, by=admin.id)
    return DataResponse(data=CategoryResponse.model_validate(category))


@router.delete(
    "/pack-categories/{category_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_pack_category(
    category_id: str,
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Delete a pack category (admin only). Fails if packs are still assigned."""
    category = await db.get(PackCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check for child categories
    child_count_r = await db.execute(
        select(func.count(PackCategory.id)).where(PackCategory.parent_id == category_id)
    )
    if child_count_r.scalar_one() > 0:
        raise HTTPException(
            status_code=422,
            detail="Cannot delete category with child categories; reassign or remove children first",
        )

    # Check for assigned packs
    assignment_count_r = await db.execute(
        select(func.count()).select_from(
            select(PackCategoryAssignment).where(
                PackCategoryAssignment.category_id == category_id
            ).subquery()
        )
    )
    if assignment_count_r.scalar_one() > 0:
        raise HTTPException(
            status_code=422,
            detail="Cannot delete category with assigned packs; unassign packs first",
        )

    await db.delete(category)
    await db.commit()
    log.info("pack_category_deleted", category_id=category_id, by=admin.id)
