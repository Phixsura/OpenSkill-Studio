"""Pack discussion/comment endpoints — threaded conversations on packs."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta, reject_ctrl_str
from app.services.discussion import DiscussionService

router = APIRouter(tags=["Discussions"])


class CreateCommentRequest(BaseModel):
    body: str
    parent_id: str | None = None

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        # R88e: NUL -> Postgres 22021 -> 500; other C0 chars would store raw
        reject_ctrl_str(v, "body")
        v = v.strip()
        if len(v) < 1 or len(v) > 5000:
            raise ValueError("Comment body must be 1-5000 characters")
        return v


class CommentResponse(BaseModel):
    id: str
    pack_id: str
    user_id: str
    parent_id: str | None
    body: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}


@router.post(
    "/registry/packs/{pack_id}/discussions",
    response_model=DataResponse[CommentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_comment(
    pack_id: str,
    body: CreateCommentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = DiscussionService(db)
    comment = await svc.create_comment(pack_id, user.id, body.body, body.parent_id)
    await db.commit()
    return DataResponse(data=CommentResponse.model_validate(comment))


@router.get(
    "/registry/packs/{pack_id}/discussions",
    response_model=ListResponse[CommentResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_comments(
    pack_id: str,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    svc = DiscussionService(db)
    comments, total = await svc.list_comments(pack_id, page, per_page)
    return ListResponse(
        data=comments,
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.delete(
    "/registry/packs/{pack_id}/discussions/{comment_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_comment(
    pack_id: str,
    comment_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = DiscussionService(db)
    await svc.delete_comment(comment_id, user.id, pack_id)
    await db.commit()
