"""Skill Pack models — reusable, versioned content bundles for AI visual training."""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# ── Enums ────────────────────────────────────────────────


class PackStatus(str, enum.Enum):
    DRAFT = "draft"  # editable, not installable
    PUBLISHED = "published"  # has ≥1 release, visible per visibility
    ARCHIVED = "archived"  # soft-deleted, existing installs unaffected


class PackVisibility(str, enum.Enum):
    PRIVATE = "private"  # only owner org sees it
    UNLISTED = "unlisted"  # accessible by direct link, not in registry
    PUBLIC = "public"  # discoverable in registry catalog


class InstallStatus(str, enum.Enum):
    ACTIVE = "active"  # tracking source pack
    FORKED = "forked"  # detached, no more updates
    REMOVED = "removed"  # uninstalled


# ── Skill Pack ───────────────────────────────────────────


class SkillPack(Base):
    __tablename__ = "skill_packs"
    __table_args__ = (
        Index("uq_pack_org_slug", "owner_org_id", "slug", unique=True),
        Index("ix_packs_visibility_status", "visibility", "status"),
        Index("ix_packs_owner", "owner_org_id"),
    )

    id: Mapped[str] = ulid_pk()
    owner_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[PackStatus] = mapped_column(
        Enum(PackStatus, name="pack_status", create_constraint=True),
        default=PackStatus.DRAFT,
    )
    visibility: Mapped[PackVisibility] = mapped_column(
        Enum(PackVisibility, name="pack_visibility", create_constraint=True),
        default=PackVisibility.PRIVATE,
    )
    language: Mapped[str] = mapped_column(String(10), default="en")
    cover_image_key: Mapped[str | None] = mapped_column(String(500))

    # Structured metadata for registry search
    learning_outcomes: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    scenario_tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    tool_tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    capability_tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    difficulty: Mapped[str | None] = mapped_column(String(20))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    prerequisite_packs: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")

    # Counters
    install_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_rating: Mapped[float | None] = mapped_column(Float, nullable=True, default=None)

    # Automated quality score (0-100), computed on publish_release
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Computed badges persisted for fast lookup (e.g. ["Popular", "New"])
    badges: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")

    # Publication approval workflow
    review_status: Mapped[str | None] = mapped_column(  # pending/approved/rejected/none
        String(20), nullable=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Cross-org sharing: when True, pack can be shared to other orgs
    sharing_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    # Provenance (author, license, attribution)
    provenance: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Pack Contents (join tables) ──────────────────────────


class SkillPackSkill(Base):
    """Join: which skills are in a pack (composite PK)."""

    __tablename__ = "skill_pack_skills"

    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class SkillPackTemplate(Base):
    """Join: which project templates are in a pack (composite PK)."""

    __tablename__ = "skill_pack_templates"

    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), primary_key=True
    )
    template_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("project_templates.id", ondelete="CASCADE"), primary_key=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


# ── Versioned Releases ───────────────────────────────────


class SkillPackRelease(Base):
    """Immutable versioned snapshot of a pack's contents."""

    __tablename__ = "skill_pack_releases"
    __table_args__ = (
        Index("uq_release_version", "pack_id", "version", unique=True),
        Index("ix_releases_pack_date", "pack_id", "released_at"),
    )

    id: Mapped[str] = ulid_pk()
    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    manifest: Mapped[dict] = mapped_column(JSONB, nullable=False)
    changelog: Mapped[str | None] = mapped_column(Text)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    component_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    released_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), nullable=False)
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ── Installation Tracking ────────────────────────────────


class SkillPackInstallation(Base):
    """Tracks that an org installed a specific pack release."""

    __tablename__ = "skill_pack_installations"
    __table_args__ = (
        Index("uq_install_org_pack", "org_id", "pack_id", unique=True),
        Index("ix_installs_org", "org_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    pack_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("skill_packs.id", ondelete="SET NULL")
    )
    release_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("skill_pack_releases.id", ondelete="SET NULL")
    )
    installed_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[InstallStatus] = mapped_column(
        Enum(InstallStatus, name="install_status", create_constraint=True),
        default=InstallStatus.ACTIVE,
    )
    installed_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id"), nullable=False)
    installed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
