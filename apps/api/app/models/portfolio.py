import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ProfileVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class ItemVisibility(str, enum.Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class UserProfile(Base):
    __tablename__ = "user_profiles"
    __table_args__ = (
        Index("ix_profiles_username", "username"),
        Index("ix_profiles_visibility", "visibility"),
    )

    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    headline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    social_links: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    visibility: Mapped[ProfileVisibility] = mapped_column(
        Enum(ProfileVisibility, name="profile_visibility", create_constraint=True),
        default=ProfileVisibility.PUBLIC,
    )
    theme: Mapped[str] = mapped_column(String(20), default="default")
    custom_og_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"
    __table_args__ = (
        Index("uq_portfolio_user_slug", "user_id", "slug", unique=True),
        Index("ix_portfolio_user_vis_order", "user_id", "visibility", "sort_order"),
        Index("ix_portfolio_user_featured", "user_id", "featured"),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    submission_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, server_default="{}")
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_org_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_project: Mapped[str | None] = mapped_column(String(200), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    show_score: Mapped[bool] = mapped_column(Boolean, default=False)
    visibility: Mapped[ItemVisibility] = mapped_column(
        Enum(ItemVisibility, name="item_visibility", create_constraint=True),
        default=ItemVisibility.PUBLIC,
    )
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SkillBadge(Base):
    __tablename__ = "skill_badges"
    __table_args__ = (
        Index("uq_badge_user_skill_org", "user_id", "skill_id", "org_id", unique=True),
        Index("ix_badges_user_show", "user_id", "show_on_profile"),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    completion_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    show_on_profile: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
