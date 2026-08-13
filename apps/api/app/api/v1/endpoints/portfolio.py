from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.base import DataResponse
from app.schemas.portfolio import (
    CreatePortfolioItemRequest,
    PortfolioItemResponse,
    ProfileResponse,
    PublicProfileResponse,
    SkillBadgeResponse,
    ToggleBadgeRequest,
    UpdatePortfolioItemRequest,
    UpdateProfileRequest,
    UsernameRequest,
)
from app.services.portfolio import PortfolioService

router = APIRouter(tags=["Portfolio"])


# ── Public (no auth) ─────────────────────────────────────


@router.get("/u/{username}", response_model=PublicProfileResponse)
async def get_public_profile(username: str, db: AsyncSession = Depends(get_db)):
    svc = PortfolioService(db)
    profile = await svc.get_public_profile(username)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Convert featured items to response format
    profile["featured_items"] = [
        PortfolioItemResponse.model_validate(i) for i in profile["featured_items"]
    ]
    return profile


@router.get("/u/{username}/items", response_model=DataResponse[list[PortfolioItemResponse]])
async def get_public_items(username: str, db: AsyncSession = Depends(get_db)):
    svc = PortfolioService(db)
    items = await svc.get_public_items(username)
    return DataResponse(data=[PortfolioItemResponse.model_validate(i) for i in items])


@router.get("/u/{username}/items/{slug}", response_model=DataResponse[PortfolioItemResponse])
async def get_public_item(username: str, slug: str, db: AsyncSession = Depends(get_db)):
    svc = PortfolioService(db)
    item = await svc.get_public_item(username, slug)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return DataResponse(data=PortfolioItemResponse.model_validate(item))


# ── Profile Management ───────────────────────────────────


@router.get("/portfolio/profile", response_model=DataResponse[ProfileResponse])
async def get_my_profile(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    profile = await svc.get_or_create_profile(user.id)
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.put("/portfolio/profile", response_model=DataResponse[ProfileResponse])
async def update_my_profile(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    profile = await svc.update_profile(user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


@router.put("/portfolio/username", response_model=DataResponse[ProfileResponse])
async def change_username(
    body: UsernameRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    profile = await svc.set_username(user.id, body.username)
    await db.commit()
    return DataResponse(data=ProfileResponse.model_validate(profile))


# ── Portfolio Items ──────────────────────────────────────


@router.get("/portfolio/items", response_model=DataResponse[list[PortfolioItemResponse]])
async def list_my_items(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    items = await svc.list_items(user.id)
    return DataResponse(data=[PortfolioItemResponse.model_validate(i) for i in items])


@router.post("/portfolio/items", response_model=DataResponse[PortfolioItemResponse], status_code=201)
async def create_item(
    body: CreatePortfolioItemRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    item = await svc.create_item(
        user.id, body.title, body.description, body.submission_id,
        body.tags, body.cover_image_url, body.external_url,
        body.visibility, body.featured,
    )
    await db.commit()
    return DataResponse(data=PortfolioItemResponse.model_validate(item))


@router.get("/portfolio/items/{item_id}", response_model=DataResponse[PortfolioItemResponse])
async def get_my_item(
    item_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    item = await svc.get_item(item_id)
    if item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return DataResponse(data=PortfolioItemResponse.model_validate(item))


@router.put("/portfolio/items/reorder", status_code=200)
async def reorder_my_items(
    body: dict,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    item_ids = body.get("item_ids", [])
    for i, iid in enumerate(item_ids):
        item = await svc.get_item(iid)
        if item.user_id == user.id:
            item.sort_order = i
    await db.commit()
    return {"message": "Items reordered"}


@router.put("/portfolio/items/{item_id}", response_model=DataResponse[PortfolioItemResponse])
async def update_my_item(
    item_id: str, body: UpdatePortfolioItemRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    item = await svc.update_item(item_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=PortfolioItemResponse.model_validate(item))


@router.delete("/portfolio/items/{item_id}", status_code=204)
async def delete_my_item(
    item_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    await svc.delete_item(item_id, user.id)
    await db.commit()


@router.post("/portfolio/upload-cover", response_model=DataResponse[dict])
async def upload_cover_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    """Upload a cover image for portfolio items. Returns the S3 URL."""
    import re

    from ulid import ULID

    from app.config import settings
    from app.core.storage import get_s3_client

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit for covers
        raise HTTPException(status_code=413, detail="Cover image must be under 10MB")

    safe_name = re.sub(r"[^\w.\-]", "_", file.filename or "cover.jpg")
    file_key = f"users/{user.id}/covers/{ULID()}_{safe_name}"

    async for client in get_s3_client():
        await client.put_object(
            Bucket=settings.s3_bucket,
            Key=file_key,
            Body=content,
            ContentType=file.content_type or "image/jpeg",
        )

    cover_url = f"{settings.s3_endpoint}/{settings.s3_bucket}/{file_key}"
    return DataResponse(data={"cover_url": cover_url})


# ── Badges ───────────────────────────────────────────────


@router.get("/portfolio/badges", response_model=DataResponse[list[SkillBadgeResponse]])
async def list_my_badges(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    badges = await svc.list_badges(user.id)
    return DataResponse(data=[
        SkillBadgeResponse(
            id=b.id, skill_name=b.skill_name, category_name=b.category_name,
            completion_pct=b.completion_pct, completed=b.completion_pct >= 100,
            show_on_profile=b.show_on_profile,
        )
        for b in badges
    ])


@router.put("/portfolio/badges/{badge_id}", response_model=DataResponse[SkillBadgeResponse])
async def toggle_badge(
    badge_id: str, body: ToggleBadgeRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    svc = PortfolioService(db)
    badge = await svc.toggle_badge(badge_id, user.id, body.show_on_profile)
    await db.commit()
    return DataResponse(data=SkillBadgeResponse(
        id=badge.id, skill_name=badge.skill_name, category_name=badge.category_name,
        completion_pct=badge.completion_pct, completed=badge.completion_pct >= 100,
        show_on_profile=badge.show_on_profile,
    ))
