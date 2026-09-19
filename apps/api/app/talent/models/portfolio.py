"""Portfolio showcase models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

PORTFOLIO_ITEM_TYPES = frozenset(
    {
        "project",
        "case_study",
        "work_sample",
        "publication",
        "presentation",
        "open_source",
        "certification_project",
        "commercial_deliverable",
        "research",
        "creative_work",
    }
)

PORTFOLIO_VISIBILITY_OPTIONS = frozenset({"private", "passport_visible", "public"})


class PortfolioItem(Base):
    __tablename__ = "talent_portfolio_items"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), index=True)
    item_type: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    capability_ids: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    pinned: Mapped[bool] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
