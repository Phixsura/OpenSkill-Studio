"""Workflow Pack models — versioned, typed AI-production workflows (ADR-010).

Mirrors the SkillPack trio (pack / immutable release / installation) so both
component families share distribution semantics. Definitions are pure data
validated against a closed step vocabulary — no code execution, ever.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
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
from app.models.skill_pack import InstallStatus, PackStatus, PackVisibility


class WorkflowPack(Base):
    """A reusable production workflow (draft definition lives here; releases snapshot it)."""

    __tablename__ = "workflow_packs"

    id: Mapped[str] = ulid_pk()
    owner_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PackStatus] = mapped_column(
        Enum(PackStatus, name="pack_status", create_constraint=False),
        default=PackStatus.DRAFT,
    )
    visibility: Mapped[PackVisibility] = mapped_column(
        Enum(PackVisibility, name="pack_visibility", create_constraint=False),
        default=PackVisibility.PRIVATE,
    )
    language: Mapped[str] = mapped_column(String(10), default="en", server_default="en")
    cover_image_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # "production" | "pipeline" | "review" — free label for registry filtering
    workflow_type: Mapped[str] = mapped_column(
        String(50), default="production", server_default="production"
    )
    scenario_tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    tool_tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    capability_tags: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    install_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    review_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    provenance: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Working definition (mutable while DRAFT; snapshots into releases)
    definition: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    # Derived caches from the definition (for registry cards / run forms)
    input_schema: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    output_schema: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    definition_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("uq_wfpack_org_slug", "owner_org_id", "slug", unique=True),
        Index("ix_wfpacks_visibility_status", "visibility", "status"),
        # D4 payload cap: definitions are bounded data, not blobs
        CheckConstraint(
            "octet_length(definition::text) <= 262144", name="ck_wfpack_definition_size"
        ),
    )


class WorkflowPackRelease(Base):
    """Immutable release snapshot — never mutated after insert (D1)."""

    __tablename__ = "workflow_pack_releases"

    id: Mapped[str] = ulid_pk()
    pack_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("workflow_packs.id", ondelete="CASCADE")
    )
    version: Mapped[str] = mapped_column(String(50))
    # {schema_version, version, name, summary, definition (no ui), dependencies, provenance}
    manifest: Mapped[dict] = mapped_column(JSONB)
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str] = mapped_column(String(64))  # sha256 of canonical manifest JSON
    step_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Structured supersession (REV-7): id of the release that replaces this one
    deprecated_by: Mapped[str | None] = mapped_column(String(26), nullable=True)
    released_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    released_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("uq_wfrelease_version", "pack_id", "version", unique=True),
        Index("ix_wfreleases_pack_date", "pack_id", "released_at"),
    )


class WorkflowPackInstallation(Base):
    """An org's installation of a workflow pack release."""

    __tablename__ = "workflow_pack_installations"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    # Nullable SET NULL — installations survive pack deletion
    pack_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("workflow_packs.id", ondelete="SET NULL"), nullable=True
    )
    release_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("workflow_pack_releases.id", ondelete="SET NULL"), nullable=True
    )
    installed_version: Mapped[str] = mapped_column(String(50))
    status: Mapped[InstallStatus] = mapped_column(
        Enum(InstallStatus, name="install_status", create_constraint=False),
        default=InstallStatus.ACTIVE,
    )
    # Forked local copy of the definition; None while tracking the release
    local_definition: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    locally_modified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    installed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    installed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("uq_wfinstall_org_pack", "org_id", "pack_id", unique=True),
        Index("ix_wfinstalls_org", "org_id"),
    )


class ComfyUIImport(Base):
    """Provenance record for an imported ComfyUI workflow. NEVER executed."""

    __tablename__ = "comfyui_imports"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    # Loose coupling — the pack draft created from this import (if any)
    pack_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    # Byte-for-byte original (parsed JSON form), immutable provenance
    original_json: Mapped[dict] = mapped_column(JSONB)
    original_sha256: Mapped[str] = mapped_column(String(64))
    format_detected: Mapped[str] = mapped_column(String(20))  # ui | api | png_embedded
    dependency_report: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    status: Mapped[str] = mapped_column(
        String(20), default="imported", server_default="imported"
    )  # imported | mapped | discarded
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_comfyui_imports_org", "org_id"),)
