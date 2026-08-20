"""Pack Review endpoints — ratings and reviews for public skill packs."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.pack_review import CreateReviewRequest, ReviewResponse
from app.services.pack_review import PackReviewService

router = APIRouter(tags=["Pack Reviews"])


@router.post(
    "/registry/packs/{pack_id}/reviews",
    response_model=DataResponse[ReviewResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(5, 60))],
)
async def create_review(
    pack_id: str,
    body: CreateReviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit a review for a public pack. One review per user per pack."""
    svc = PackReviewService(db)
    review = await svc.create_review(
        pack_id=pack_id,
        user_id=user.id,
        rating=body.rating,
        title=body.title,
        body=body.body,
    )
    await db.commit()
    return DataResponse(data=ReviewResponse.model_validate(review))


@router.get(
    "/registry/packs/{pack_id}/reviews",
    response_model=ListResponse[ReviewResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_reviews(
    pack_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List reviews for a pack. No authentication required."""
    svc = PackReviewService(db)
    reviews, total = await svc.list_reviews(pack_id, page, per_page)
    return ListResponse(
        data=[ReviewResponse.model_validate(r) for r in reviews],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.delete(
    "/registry/packs/{pack_id}/reviews/{review_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_review(
    pack_id: str,
    review_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete your own review. Owner only."""
    svc = PackReviewService(db)
    await svc.delete_review(review_id, user.id)
    await db.commit()
