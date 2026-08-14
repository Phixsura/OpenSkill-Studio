"""Portfolio service — profiles, items, badges, public pages."""

import re
import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.portfolio import (
    ItemVisibility,
    PortfolioItem,
    ProfileVisibility,
    SkillBadge,
    UserProfile,
)
from app.models.project import Submission, SubmissionStatus
from app.models.user import User
from app.schemas.portfolio import RESERVED_USERNAMES

log = structlog.get_logger()


# ── Errors ────────────────────────────────────────────────────


class ProfileNotFoundError(AppError):
    def __init__(self):
        super().__init__("PROFILE_NOT_FOUND", "Profile not found", 404)


class UsernameUnavailableError(AppError):
    def __init__(self):
        super().__init__("USERNAME_UNAVAILABLE", "This username is already taken", 409)


class ItemNotFoundError(AppError):
    def __init__(self):
        super().__init__("ITEM_NOT_FOUND", "Portfolio item not found", 404)


# ── Service ───────────────────────────────────────────────────


class PortfolioService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Profile ──

    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        profile = await self.db.get(UserProfile, user_id)
        if profile is not None:
            return profile

        # Auto-generate username from user
        user = await self.db.get(User, user_id)
        if user is None:
            raise AppError("USER_NOT_FOUND", "User not found", 404)

        base = re.sub(r"[^a-z0-9]+", "-", user.display_name.lower()).strip("-")
        if not base or len(base) < 3:
            base = f"user-{secrets.token_hex(3)}"
        username = base[:40]

        # Ensure uniqueness
        while True:
            existing = await self.db.execute(
                select(UserProfile).where(UserProfile.username == username)
            )
            if existing.scalar_one_or_none() is None and username not in RESERVED_USERNAMES:
                break
            username = f"{base[:30]}-{secrets.token_hex(3)}"

        profile = UserProfile(user_id=user_id, username=username)
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def update_profile(self, user_id: str, **fields) -> UserProfile:
        profile = await self.get_or_create_profile(user_id)
        for k, v in fields.items():
            if v is not None and hasattr(profile, k):
                setattr(profile, k, v)
        await self.db.flush()
        return profile

    async def set_username(self, user_id: str, username: str) -> UserProfile:
        # Check uniqueness
        existing = await self.db.execute(
            select(UserProfile).where(
                UserProfile.username == username,
                UserProfile.user_id != user_id,
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise UsernameUnavailableError() from None

        profile = await self.get_or_create_profile(user_id)
        profile.username = username
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise UsernameUnavailableError() from None
        return profile

    # ── Public ──

    async def get_public_profile(self, username: str) -> dict | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.username == username))
        profile = result.scalar_one_or_none()
        if profile is None or profile.visibility != ProfileVisibility.PUBLIC:
            return None

        user = await self.db.get(User, profile.user_id)
        if user is None:
            return None  # pragma: no cover

        # Get skills (visible badges)
        badges = await self.db.execute(
            select(SkillBadge).where(
                SkillBadge.user_id == profile.user_id,
                SkillBadge.show_on_profile == True,  # noqa: E712
            )
        )
        skills = [
            {
                "name": b.skill_name,
                "category": b.category_name,
                "completion_pct": b.completion_pct,
                "completed": b.completion_pct >= 100,
            }
            for b in badges.scalars()
        ]

        # Get featured items (public only)
        items_result = await self.db.execute(
            select(PortfolioItem)
            .where(
                PortfolioItem.user_id == profile.user_id,
                PortfolioItem.visibility == ItemVisibility.PUBLIC,
                PortfolioItem.featured == True,  # noqa: E712
            )
            .order_by(PortfolioItem.sort_order)
        )
        featured = list(items_result.scalars().all())

        # Count all public items
        count_result = await self.db.execute(
            select(func.count(PortfolioItem.id)).where(
                PortfolioItem.user_id == profile.user_id,
                PortfolioItem.visibility == ItemVisibility.PUBLIC,
            )
        )
        item_count = count_result.scalar_one()

        return {
            "username": profile.username,
            "display_name": user.display_name,
            "headline": profile.headline,
            "bio": profile.bio,
            "avatar_url": user.avatar_url,
            "location": profile.location,
            "website_url": profile.website_url,
            "social_links": profile.social_links or {},
            "skills": skills,
            "featured_items": featured,
            "item_count": item_count,
            "joined_at": user.created_at,
        }

    async def get_public_items(self, username: str) -> list[PortfolioItem]:
        result = await self.db.execute(select(UserProfile).where(UserProfile.username == username))
        profile = result.scalar_one_or_none()
        if profile is None or profile.visibility != ProfileVisibility.PUBLIC:
            return []

        items_result = await self.db.execute(
            select(PortfolioItem)
            .where(
                PortfolioItem.user_id == profile.user_id,
                PortfolioItem.visibility == ItemVisibility.PUBLIC,
            )
            .order_by(PortfolioItem.sort_order)
        )
        return list(items_result.scalars().all())

    async def get_public_item(self, username: str, slug: str) -> PortfolioItem | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.username == username))
        profile = result.scalar_one_or_none()
        if profile is None:
            return None  # pragma: no cover

        item_result = await self.db.execute(
            select(PortfolioItem).where(
                PortfolioItem.user_id == profile.user_id,
                PortfolioItem.slug == slug,
                PortfolioItem.visibility.in_([ItemVisibility.PUBLIC, ItemVisibility.UNLISTED]),
            )
        )
        return item_result.scalar_one_or_none()

    # ── Items ──

    async def create_item(
        self,
        user_id: str,
        title: str,
        description: str | None,
        submission_id: str | None,
        tags: list[str] | None,
        cover_image_url: str | None,
        external_url: str | None,
        visibility: str,
        featured: bool,
    ) -> PortfolioItem:
        slug = self._generate_slug(title)

        source_org_name = None
        source_project = None
        score = None

        if submission_id:
            submission = await self.db.get(Submission, submission_id)
            if submission is None or submission.user_id != user_id:
                raise AppError("SUBMISSION_NOT_FOUND", "Submission not found or not yours", 404)
            if submission.status != SubmissionStatus.APPROVED:
                raise AppError("SUBMISSION_NOT_APPROVED", "Submission must be approved", 422)
            score = submission.final_score

            # Denormalize org/project names
            from app.models.organization import Organization
            from app.models.project import Project

            project = await self.db.get(Project, submission.project_id)
            if project:
                source_project = project.title
                org = await self.db.get(Organization, project.org_id)
                if org:
                    source_org_name = org.name

        try:
            vis = ItemVisibility(visibility)
        except ValueError:
            vis = ItemVisibility.PUBLIC

        item = PortfolioItem(
            user_id=user_id,
            submission_id=submission_id,
            title=title,
            slug=slug,
            description=description,
            cover_image_url=cover_image_url,
            tags=tags or [],
            external_url=external_url,
            source_org_name=source_org_name,
            source_project=source_project,
            score=score,
            visibility=vis,
            featured=featured,
            published_at=datetime.now(UTC),
        )
        self.db.add(item)
        await self.db.flush()
        return item

    async def list_items(self, user_id: str) -> list[PortfolioItem]:
        result = await self.db.execute(
            select(PortfolioItem)
            .where(PortfolioItem.user_id == user_id)
            .order_by(PortfolioItem.sort_order, PortfolioItem.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_item(self, item_id: str) -> PortfolioItem:
        item = await self.db.get(PortfolioItem, item_id)
        if item is None:
            raise ItemNotFoundError()
        return item

    async def update_item(self, item_id: str, user_id: str, **fields) -> PortfolioItem:
        item = await self.get_item(item_id)
        if item.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your item", 403)
        for k, v in fields.items():
            if v is not None and hasattr(item, k):
                setattr(item, k, v)
        await self.db.flush()
        return item

    async def delete_item(self, item_id: str, user_id: str) -> None:
        item = await self.get_item(item_id)
        if item.user_id != user_id:
            raise AppError("PERMISSION_DENIED", "Not your item", 403)
        await self.db.delete(item)
        await self.db.flush()

    # ── Badges ──

    async def list_badges(self, user_id: str) -> list[SkillBadge]:
        result = await self.db.execute(
            select(SkillBadge)
            .where(SkillBadge.user_id == user_id)
            .order_by(SkillBadge.category_name, SkillBadge.skill_name)
        )
        return list(result.scalars().all())

    async def toggle_badge(self, badge_id: str, user_id: str, show: bool) -> SkillBadge:
        badge = await self.db.get(SkillBadge, badge_id)
        if badge is None or badge.user_id != user_id:
            raise AppError("BADGE_NOT_FOUND", "Badge not found", 404)
        badge.show_on_profile = show
        await self.db.flush()
        return badge

    # ── Helpers ──

    @staticmethod
    def _generate_slug(name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if len(slug) < 3:
            slug = f"{slug}-{secrets.token_hex(3)}"
        return slug[:200]
