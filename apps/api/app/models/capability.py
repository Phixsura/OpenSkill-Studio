"""Capability taxonomy — the universal join key across workflows, providers, matching.

Platform-governed closed vocabulary seeded via migration (NOT a Python enum) so it
can be extended through curated migrations or org-scoped `x-<org>.` extensions
without code deploys. See ADR-011.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class CapabilityTag(Base):
    """A named AI capability (e.g. image_generation) with a typed I/O signature.

    Workflow steps reference capabilities — never vendors — so workflows stay
    replaceable as AI tools change (Issue #21 Part B §7).
    """

    __tablename__ = "capability_tags"

    id: Mapped[str] = ulid_pk()
    # Platform keys: "image_generation". Org extensions: "x-{org_slug}.custom_cap"
    key: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # generation | editing | review | audio | utility
    category: Mapped[str] = mapped_column(String(30), default="generation")
    # Bumped when the capability contract (feature keys) changes
    contract_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    # {"inputs": ["image", "prompt"], "outputs": ["video"]} — machine-readable I/O
    io_signature: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    is_platform: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    # Only set for org extensions (x-... keys)
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_capability_category", "category"),)
