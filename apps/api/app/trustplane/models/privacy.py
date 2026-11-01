"""Data Privacy & Consent Controls models (ADR-017 Part G).

Privacy reviews for AI data flows — purpose limitation, minimization,
classification, redaction hooks, consent references, retention, and
cross-region transfer constraints.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class PrivacyReviewStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"


class DataClassification(str, enum.Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SENSITIVE_PII = "sensitive_pii"
    HIGHLY_SENSITIVE = "highly_sensitive"


class LegalBasis(str, enum.Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTEREST = "vital_interest"
    PUBLIC_INTEREST = "public_interest"
    LEGITIMATE_INTEREST = "legitimate_interest"


class ConsentStatus(str, enum.Enum):
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    NOT_REQUIRED = "not_required"


# ── Models ───────────────────────────────────────────────────────────


class PrivacyReview(Base):
    """Privacy review for an AI system's data flows."""

    __tablename__ = "trust_privacy_reviews"
    __table_args__ = (
        Index("ix_trust_privacy_org", "org_id"),
        Index("ix_trust_privacy_system", "system_id"),
        Index("ix_trust_privacy_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    status: Mapped[PrivacyReviewStatus] = mapped_column(
        Enum(PrivacyReviewStatus, name="trust_privacy_review_status", create_constraint=True),
        nullable=False,
        default=PrivacyReviewStatus.DRAFT,
    )
    # Data flow analysis
    data_inputs: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )  # [{source, classification, purpose, retention}]
    data_outputs: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    data_classification: Mapped[DataClassification] = mapped_column(
        Enum(DataClassification, name="trust_data_classification", create_constraint=True),
        nullable=False,
        default=DataClassification.INTERNAL,
    )
    # Privacy controls
    purpose_limitation: Mapped[str | None] = mapped_column(Text, nullable=True)
    minimization_measures: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    redaction_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    retention_policy: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Legal basis
    legal_basis: Mapped[LegalBasis | None] = mapped_column(
        Enum(LegalBasis, name="trust_legal_basis", create_constraint=True), nullable=True
    )
    legal_basis_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Cross-region
    regions: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    cross_region_transfers: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )  # [{from_region, to_region, mechanism, justification}]
    # Provider data use
    provider_data_use: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # People
    reviewed_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConsentRecord(Base):
    """Consent/legal-basis reference for AI data processing."""

    __tablename__ = "trust_consent_records"
    __table_args__ = (
        Index("ix_trust_consent_org", "org_id"),
        Index("ix_trust_consent_system", "system_id"),
        Index("ix_trust_consent_status", "consent_status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    system_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trust_ai_systems.id", ondelete="CASCADE"), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(300), nullable=False)
    consent_status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus, name="trust_consent_status", create_constraint=True),
        nullable=False,
    )
    data_categories: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, default=dict, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
