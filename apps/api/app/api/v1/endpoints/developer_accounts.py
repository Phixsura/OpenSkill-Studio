"""Developer Account management endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_user_or_app, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.developer import (
    CreateDeveloperAccountRequest,
    DeveloperAccountResponse,
    UpdateDeveloperAccountRequest,
)
from app.services import developer as dev_svc

router = APIRouter(tags=["Developer Accounts"])


@router.post(
    "/developer/accounts",
    response_model=DataResponse[DeveloperAccountResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def create_developer_account(
    body: CreateDeveloperAccountRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register a new developer account."""
    # Validate org membership if org_id provided
    if body.org_id:
        from app.models.organization import OrgRole

        await require_org_member(body.org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    account = await dev_svc.create_developer_account(
        db,
        owner_user_id=user.id,
        display_name=body.display_name,
        slug=body.slug,
        website_url=body.website_url,
        support_email=body.support_email,
        org_id=body.org_id,
    )
    await db.commit()
    return DataResponse(data=DeveloperAccountResponse.model_validate(account))


@router.get(
    "/developer/accounts/me",
    response_model=DataResponse[DeveloperAccountResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_my_developer_account(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_or_app),
):
    """Get the current user's developer account."""
    account = await dev_svc.get_developer_account_by_user(db, user.id)
    if not account:
        raise dev_svc.DeveloperNotFoundError()
    return DataResponse(data=DeveloperAccountResponse.model_validate(account))


@router.get(
    "/developer/accounts/{account_id}",
    response_model=DataResponse[DeveloperAccountResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_developer_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_or_app),
):
    """Get a developer account by ID."""
    account = await dev_svc.get_developer_account(db, account_id)
    return DataResponse(data=DeveloperAccountResponse.model_validate(account))


@router.patch(
    "/developer/accounts/{account_id}",
    response_model=DataResponse[DeveloperAccountResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def update_developer_account(
    account_id: str,
    body: UpdateDeveloperAccountRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a developer account (owner only)."""
    account = await dev_svc.get_developer_account(db, account_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    updates = body.model_dump(exclude_unset=True)
    account = await dev_svc.update_developer_account(db, account, **updates)
    resp = DeveloperAccountResponse.model_validate(account)
    await db.commit()
    return DataResponse(data=resp)


@router.get(
    "/developer/accounts",
    response_model=ListResponse[DeveloperAccountResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_developer_accounts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_or_app),
):
    """List developer accounts (platform visibility)."""
    accounts, total = await dev_svc.list_developer_accounts(db, page=page, per_page=per_page)
    return ListResponse(
        data=[DeveloperAccountResponse.model_validate(a) for a in accounts],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )
