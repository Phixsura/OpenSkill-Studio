import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole, UserStatus
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.user import AdminUpdateRoleRequest, AdminUserResponse

log = structlog.get_logger()

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=ListResponse[AdminUserResponse],
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def list_users(
    page: int = 1,
    per_page: int = 20,
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
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return DataResponse(data=AdminUserResponse.model_validate(user))


@router.put(
    "/users/{user_id}/role",
    response_model=DataResponse[AdminUserResponse],
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

    user.status = UserStatus.DELETED
    await db.commit()
