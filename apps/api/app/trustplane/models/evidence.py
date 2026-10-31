"""Assurance Case & Evidence Graph models (ADR-017 Part C).

Assurance cases link claims to evidence items via a many-to-many graph.
Evidence items are versioned and carry provenance, scope, expiry and
integrity metadata. Missing, stale, or conflicting evidence is visible.
"""

import enum
from datetime import datetime

from sqlalchemy import (
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


class ClaimStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CHALLENGED = "challenged"  # conflicting evidence found
    RETIRED = "retired"


class EvidenceType(str, enum.Enum):
    BENCHMARK = "benchmark"
    EXPERIMENT = "experiment"
    EVALUATION = "evaluation"
    RED_TEAM = "red_team"
    APP_REVIEW = "app_review"
    PRIVACY_ASSESSMENT = "privacy_assessment"
    INCIDENT_REPORT = "incident_report"
    HUMAN_ATTESTATION = "human_attestation"
    EXTERNAL_AUDIT = "external_audit"
    POLICY_SIMULATION = "policy_simulation"
    CUSTOM = "custom"


class EvidenceStatus(str, enum.Enum):
    DRAFT = "draft"
    VALID = "valid"
    STALE = "stale"      # expired or source changed
    REVOKED = "revoked"  # explicitly invalidated
    SUPERSEDED = "superseded"


class LinkRelation(str, enum.Enum):
    SUPPORTS = "supports"
    WEAKENS = "weakens"
    MITIGATES = "mitigates"
    DEPENDS_ON = "depends_on"


# ── Models ───────────────────────────────────────────────────────────


class AssuranceCase(Base):
    """A claim about an AI system's safety/quality property."""

    __tablename__ = "trust_assurance_cases"
    __table_args__ = (
        Index("ix_trust_case_system", "system_id"),
        Index("ix_trust_case_org_status", "org_id", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(
        Enum(ClaimStatus, name="trust_claim_status", create_constraint=True),
        nullable=False,
        default=ClaimStatus.DRAFT,
    )
    owner_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EvidenceItem(Base):
    """A piece of evidence supporting or weakening an assurance claim."""

    __tablename__ = "trust_evidence_items"
    __table_args__ = (
        Index("ix_trust_evidence_org", "org_id"),
        Index("ix_trust_evidence_type_status", "evidence_type", "status"),
        Index("ix_trust_evidence_source", "source_type", "source_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType, name="trust_evidence_type", create_constraint=True), nullable=False
    )
    status: Mapped[EvidenceStatus] = mapped_column(
        Enum(EvidenceStatus, name="trust_evidence_status", create_constraint=True),
        nullable=False,
        default=EvidenceStatus.DRAFT,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    # Provenance — loose coupling to source system
    source_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Scope & validity
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revalidation_rule: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Content & integrity
    content: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256
    # Ownership
    collected_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EvidenceLink(Base):
    """Many-to-many link between assurance cases and evidence items."""

    __tablename__ = "trust_evidence_links"
    __table_args__ = (
        Index("uq_trust_evidence_link", "case_id", "evidence_id", unique=True),
        Index("ix_trust_link_evidence", "evidence_id"),
    )

    id: Mapped[str] = ulid_pk()
    case_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_assurance_cases.id", ondelete="CASCADE"), nullable=False
    )
    evidence_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_evidence_items.id", ondelete="CASCADE"), nullable=False
    )
    relation: Mapped[LinkRelation] = mapped_column(
        Enum(LinkRelation, name="trust_link_relation", create_constraint=True),
        nullable=False,
        default=LinkRelation.SUPPORTS,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    linked_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
