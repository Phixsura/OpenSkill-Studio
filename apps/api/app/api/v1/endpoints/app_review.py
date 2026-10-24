"""App review, signing key, and OAuth endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.core.rate_limit import rate_limit
from app.models.user import User, UserRole
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.developer import (
    AppReviewResponse,
    RegisterSigningKeyRequest,
    ReviewDecisionRequest,
    SigningKeyResponse,
    SubmitForReviewRequest,
)
from app.services import developer as dev_svc

router = APIRouter(tags=["App Review"])


# ── Review Submission ────────────────────────────────────


@router.post(
    "/developer/apps/{app_id}/reviews",
    response_model=DataResponse[AppReviewResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def submit_for_review(
    app_id: str,
    body: SubmitForReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit an app version for platform review."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()

    # Validate version belongs to this app
    version = await dev_svc.get_app_version(db, body.app_version_id)
    if version.app_id != app_id:
        raise dev_svc.AppVersionNotFoundError()

    review = await dev_svc.submit_for_review(
        db,
        app_id=app_id,
        app_version_id=body.app_version_id,
        submitted_by=user.id,
        notes=body.notes,
    )
    await db.commit()
    return DataResponse(data=AppReviewResponse.model_validate(review))


@router.get(
    "/developer/apps/{app_id}/reviews",
    response_model=ListResponse[AppReviewResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_reviews(
    app_id: str,
    status: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List review submissions for an app (owner only)."""
    app = await dev_svc.get_app(db, app_id)
    account = await dev_svc.get_developer_account(db, app.developer_id)
    if account.owner_user_id != user.id:
        raise dev_svc.PermissionDeniedError()
    reviews, total = await dev_svc.list_review_submissions(
        db, app_id=app_id, status=status, page=page, per_page=per_page
    )
    return ListResponse(
        data=[AppReviewResponse.model_validate(r) for r in reviews],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


# ── Review Queue (platform admin) ───────────────────────


@router.get(
    "/admin/app-reviews",
    response_model=ListResponse[AppReviewResponse],
    dependencies=[Depends(rate_limit(120, 60))],
)
async def list_review_queue(
    status: str = "pending",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """List pending reviews across all apps (admin only)."""
    reviews, total = await dev_svc.list_review_submissions(
        db, status=status, page=page, per_page=per_page
    )
    return ListResponse(
        data=[AppReviewResponse.model_validate(r) for r in reviews],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.post(
    "/admin/app-reviews/{review_id}/decide",
    response_model=DataResponse[AppReviewResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def decide_review(
    review_id: str,
    body: ReviewDecisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Approve or reject an app review (admin only)."""
    from sqlalchemy import select

    from app.models.developer import AppReviewSubmission

    result = await db.execute(
        select(AppReviewSubmission).where(AppReviewSubmission.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        from app.exceptions import AppError

        raise AppError(status_code=404, code="REVIEW_NOT_FOUND", message="Review not found")

    review = await dev_svc.decide_review(
        db,
        review,
        decision=body.decision,
        reviewer_id=user.id,
        notes=body.notes,
    )
    await db.commit()
    return DataResponse(data=AppReviewResponse.model_validate(review))


# ── Signing Keys ─────────────────────────────────────────


@router.post(
    "/developer/signing-keys",
    response_model=DataResponse[SigningKeyResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def register_signing_key(
    body: RegisterSigningKeyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Register an Ed25519 public key for signing app packages."""
    account = await dev_svc.get_developer_account_by_user(db, user.id)
    if not account:
        raise dev_svc.DeveloperNotFoundError(
            message="You must create a developer account first"
        )
    key = await dev_svc.register_signing_key(
        db,
        developer_id=account.id,
        public_key=body.public_key,
        name=body.name,
    )
    await db.commit()
    return DataResponse(data=SigningKeyResponse.model_validate(key))


@router.get(
    "/developer/signing-keys",
    response_model=DataResponse[list[SigningKeyResponse]],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_signing_keys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List signing keys for the current developer account."""
    account = await dev_svc.get_developer_account_by_user(db, user.id)
    if not account:
        raise dev_svc.DeveloperNotFoundError()
    keys = await dev_svc.list_signing_keys(db, account.id)
    return DataResponse(data=[SigningKeyResponse.model_validate(k) for k in keys])
