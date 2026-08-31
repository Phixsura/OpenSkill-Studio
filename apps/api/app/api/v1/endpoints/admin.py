import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.core.rate_limit import rate_limit
from app.exceptions import AppError
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
    page: int = Query(default=1, ge=1, le=1_000_000),
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
        raise HTTPException(
            status_code=409, detail="Category with this slug already exists"
        ) from None
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

    # exclude_unset (not exclude_none): an explicit `"parent_id": null` must
    # clear the parent (move to root), while an absent field leaves it
    # unchanged — exclude_none made the two indistinguishable, so a child
    # category could never be moved back to root (same for clearing icon).
    update_data = body.model_dump(exclude_unset=True)

    # Validate parent if being changed to a non-null value
    if update_data.get("parent_id") is not None:
        new_parent_id = update_data["parent_id"]
        if new_parent_id == category_id:
            raise HTTPException(status_code=422, detail="Category cannot be its own parent")
        parent = await db.get(PackCategory, new_parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")
        # Walk the proposed parent's ancestor chain (bounded): re-parenting
        # under one's own descendant (A->B then B->A) creates a cycle that
        # removes both nodes from the root listing and blocks deletion.
        ancestor = parent
        chain_resolved = False
        for _ in range(100):
            if ancestor.parent_id is None:
                chain_resolved = True
                break
            if ancestor.parent_id == category_id:
                raise AppError(
                    "CATEGORY_CYCLE",
                    "Cannot set parent: it is a descendant of this category",
                    422,
                )
            ancestor = await db.get(PackCategory, ancestor.parent_id)
            if ancestor is None:
                chain_resolved = True  # dangling parent = chain ends, no cycle
                break
        if not chain_resolved:
            # Bound exceeded without reaching a root: either the chain is
            # already cyclic or deeper than any legitimate taxonomy — REJECT,
            # don't silently accept (a silent break resurrects the cycle bug
            # through a >100-deep chain)
            raise AppError(
                "CATEGORY_CYCLE",
                "Cannot set parent: ancestor chain is too deep to verify (max 100)",
                422,
            )

    for field, value in update_data.items():
        # Only parent_id and icon are nullable columns — an explicit null on
        # name/slug/sort_order would 500 at flush, so treat it as "unchanged"
        if value is None and field not in ("parent_id", "icon"):
            continue
        setattr(category, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="Category with this slug already exists"
        ) from None
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
            select(PackCategoryAssignment)
            .where(PackCategoryAssignment.category_id == category_id)
            .subquery()
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


# ── Workflow sweeper (manual/cron trigger) ────────────────


@router.post(
    "/workflows/sweep",
    dependencies=[Depends(rate_limit(6, 60))],
)
async def sweep_workflows(
    admin: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Platform-wide sweep: recover expired executor leases + expire overdue
    reviews across ALL orgs, then re-dispatch every touched run.

    The lazy sweep (run-detail reads) only fires for orgs whose runs someone
    is actually viewing — this is the operator/cron path for the rest.
    """
    from app.services.workflow_runtime import dispatch_advance, sweep_stale

    swept = await sweep_stale(db, org_id=None)
    await db.commit()
    for run_id in swept["run_ids"]:
        dispatch_advance(run_id)
    log.info(
        "workflow_sweep_manual",
        by=admin.id,
        expired_leases=swept["expired_leases"],
        expired_reviews=swept["expired_reviews"],
        stalled_runs=swept.get("stalled_runs", 0),
        runs_redispatched=len(swept["run_ids"]),
    )
    return {
        "data": {
            "expired_leases": swept["expired_leases"],
            "expired_reviews": swept["expired_reviews"],
            "stalled_runs": swept.get("stalled_runs", 0),
            "runs_redispatched": len(swept["run_ids"]),
        }
    }
