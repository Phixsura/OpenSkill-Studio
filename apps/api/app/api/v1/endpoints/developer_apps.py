"""Developer App CRUD, versioning, and lifecycle endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.developer import (
    AppResponse,
    AppSummaryResponse,
    AppVersionResponse,
    CreateAppRequest,
    CreateAppVersionRequest,
    UpdateAppRequest,
)
from app.services import developer as dev_svc

router = APIRouter(tags=["Developer Apps"])


# ── App CRUD ─────────────────────────────────────────────


@router.post(
    "/developer/apps",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def create_app(
    body: CreateAppRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new developer app."""
    account = await dev_svc.get_developer_account_by_user(db, user.id)
    if not account:
        raise dev_svc.DeveloperNotFoundError(
            message="You must create a developer account first"
        )
    app, oauth_secret = await dev_svc.create_app(
        db,
        developer_id=account.id,
        name=body.name,
        slug=body.slug,
        description=body.description,
        category=body.category,
        visibility=body.visibility,
        icon_url=body.icon_url,
        homepage_url=body.homepage_url,
        privacy_policy_url=body.privacy_policy_url,
        redirect_uris=body.redirect_uris,
        webhook_url=body.webhook_url,
        manifest=body.manifest,
    )
    await db.commit()
    return DataResponse(data=AppResponse.model_validate(app))


@router.get(
    "/developer/apps/{app_id}",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get app details."""
    app = await dev_svc.get_app(db, app_id)
    return DataResponse(data=AppResponse.model_validate(app))


@router.patch(
    "/developer/apps/{app_id}",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def update_app(
    app_id: str,
    body: UpdateAppRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update an app (developer owner only)."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    updates = body.model_dump(exclude_unset=True)
    app = await dev_svc.update_app(db, app, **updates)
    resp = AppResponse.model_validate(app)
    await db.commit()
    return DataResponse(data=resp)


@router.get(
    "/developer/apps",
    response_model=ListResponse[AppSummaryResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_apps(
    developer_id: str | None = None,
    category: str | None = None,
    status: str | None = None,
    visibility: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List apps with optional filters."""
    apps, total = await dev_svc.list_apps(
        db,
        developer_id=developer_id,
        category=category,
        status=status,
        visibility=visibility,
        page=page,
        per_page=per_page,
    )
    return ListResponse(
        data=[AppSummaryResponse.model_validate(a) for a in apps],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


# ── App Lifecycle ────────────────────────────────────────


@router.post(
    "/developer/apps/{app_id}/submit",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def submit_app_for_review(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit app for platform review."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    app = await dev_svc.transition_app_status(db, app, "submitted")
    await db.commit()
    return DataResponse(data=AppResponse.model_validate(app))


@router.post(
    "/developer/apps/{app_id}/publish",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def publish_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Publish an approved app."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    app = await dev_svc.transition_app_status(db, app, "published")
    await db.commit()
    return DataResponse(data=AppResponse.model_validate(app))


@router.post(
    "/developer/apps/{app_id}/deprecate",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def deprecate_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Deprecate an app (no new installs)."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    app = await dev_svc.transition_app_status(db, app, "deprecated")
    await db.commit()
    return DataResponse(data=AppResponse.model_validate(app))


@router.post(
    "/developer/apps/{app_id}/revoke",
    response_model=DataResponse[AppResponse],
    dependencies=[Depends(rate_limit(5, 60))],
)
async def revoke_app(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Emergency revoke — suspends all installations."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    app = await dev_svc.revoke_app(db, app_id, reason="developer_initiated")
    await db.commit()
    return DataResponse(data=AppResponse.model_validate(app))


# ── App Versions ─────────────────────────────────────────


@router.post(
    "/developer/apps/{app_id}/versions",
    response_model=DataResponse[AppVersionResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_app_version(
    app_id: str,
    body: CreateAppVersionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new app version."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    version = await dev_svc.create_app_version(
        db,
        app_id=app_id,
        version=body.version,
        manifest=body.manifest,
        changelog=body.changelog,
        content_hash=body.content_hash,
        signature=body.signature,
        min_platform_version=body.min_platform_version,
    )
    await db.commit()
    return DataResponse(data=AppVersionResponse.model_validate(version))


@router.get(
    "/developer/apps/{app_id}/versions",
    response_model=ListResponse[AppVersionResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_app_versions(
    app_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List versions for an app."""
    versions, total = await dev_svc.list_app_versions(db, app_id, page=page, per_page=per_page)
    return ListResponse(
        data=[AppVersionResponse.model_validate(v) for v in versions],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.get(
    "/developer/apps/{app_id}/versions/{version_id}",
    response_model=DataResponse[AppVersionResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def get_app_version(
    app_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a specific app version."""
    version = await dev_svc.get_app_version(db, version_id)
    return DataResponse(data=AppVersionResponse.model_validate(version))
