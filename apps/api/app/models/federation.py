"""Federation models — cross-instance registry, credential trust, talent mobility (ADR-017).

Entities: LocalInstanceIdentity, FederationInstance, TrustPolicy,
FederatedArtifact, FederatedCredentialVerification, FederatedAccountLink,
PortabilityRecord, FederatedOpportunity, FederatedMarketplaceListing,
FederatedEntitlementGrant, FederatedEcosystemObservation, FederationGrant,
FederationRevocation, DataResidencyPolicy, PeerReputationScore, PeerIncident,
FederationSearchCache, FederationCircuitBreaker.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
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


class InstanceTrustStatus(str, enum.Enum):
    PENDING = "pending"
    TRUSTED = "trusted"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


class TrustArtifactType(str, enum.Enum):
    REGISTRY_ARTIFACT = "registry_artifact"
    CREDENTIAL = "credential"
    OPPORTUNITY = "opportunity"
    MARKETPLACE_LISTING = "marketplace_listing"
    ECOSYSTEM_OBSERVATION = "ecosystem_observation"
    ALL = "all"


class TrustAction(str, enum.Enum):
    ACCEPT = "accept"
    MIRROR = "mirror"
    REJECT = "reject"


class FederatedArtifactType(str, enum.Enum):
    SKILL_PACK = "skill_pack"
    WORKFLOW_PACK = "workflow_pack"
    BENCHMARK_SUITE = "benchmark_suite"
    DEVELOPER_APP = "developer_app"


class MirrorStatus(str, enum.Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    STALE = "stale"


class CredentialType(str, enum.Enum):
    CERTIFICATE = "certificate"
    SKILL_ASSESSMENT = "skill_assessment"
    PORTFOLIO_ENDORSEMENT = "portfolio_endorsement"
    LEARNING_PATH_COMPLETION = "learning_path_completion"


class VerificationStatus(str, enum.Enum):
    VERIFIED = "verified"
    INVALID_SIGNATURE = "invalid_signature"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


class AccountLinkStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REVOKED = "revoked"


class PortabilityRecordType(str, enum.Enum):
    CREDENTIAL_EXPORT = "credential_export"
    PORTFOLIO_SNAPSHOT = "portfolio_snapshot"
    SKILL_SUMMARY = "skill_summary"


class OpportunityStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    WITHDRAWN = "withdrawn"


class ListingStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"


class EntitlementGrantStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class SettlementStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


class ObservationStatus(str, enum.Enum):
    ACTIVE = "active"
    DISPUTED = "disputed"
    RETRACTED = "retracted"


class FederationGrantType(str, enum.Enum):
    REVIEWER = "reviewer"
    INSTRUCTOR = "instructor"
    CLIENT = "client"
    OBSERVER = "observer"


class FederationGrantStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class RevocationType(str, enum.Enum):
    CREDENTIAL = "credential"
    APP = "app"
    COMPONENT_SIGNATURE = "component_signature"
    INSTANCE_KEY = "instance_key"


class ResidencyPolicyType(str, enum.Enum):
    REGION_RESTRICT = "region_restrict"
    JURISDICTION_RESTRICT = "jurisdiction_restrict"
    RETENTION_LIMIT = "retention_limit"
    CROSS_BORDER_BLOCK = "cross_border_block"


class ResidencyEnforcement(str, enum.Enum):
    BLOCK = "block"
    WARN = "warn"
    AUDIT_ONLY = "audit_only"


class IncidentType(str, enum.Enum):
    INVALID_SIGNATURE = "invalid_signature"
    SPAM = "spam"
    POLICY_VIOLATION = "policy_violation"
    REVOCATION_FLOOD = "revocation_flood"
    TIMEOUT_FLOOD = "timeout_flood"


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Part A — Instance Identity ───────────────────────────


class LocalInstanceIdentity(Base):
    """Singleton row holding this deployment's cryptographic identity."""

    __tablename__ = "local_instance_identity"

    id: Mapped[str] = mapped_column(String(26), primary_key=True, default="self")
    instance_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    signing_key_pem: Mapped[str] = mapped_column(Text, nullable=False)
    public_key_pem: Mapped[str] = mapped_column(Text, nullable=False)
    key_id: Mapped[str] = mapped_column(String(64), nullable=False)
    key_generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    previous_signing_key_pem: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_key_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_key_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    protocol_version: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="1.0"
    )
    extra_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class FederationInstance(Base):
    """A known peer OpenSkill deployment."""

    __tablename__ = "federation_instances"
    __table_args__ = (
        Index("uq_fed_instance_uri", "instance_uri", unique=True),
        Index("ix_fed_instance_trust", "trust_status"),
        Index("ix_fed_instance_key_id", "key_id"),
    )

    id: Mapped[str] = ulid_pk()
    instance_uri: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    software_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    protocol_version: Mapped[str] = mapped_column(String(10), nullable=False)
    public_key_pem: Mapped[str] = mapped_column(Text, nullable=False)
    key_id: Mapped[str] = mapped_column(String(64), nullable=False)
    key_rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    previous_key_pem: Mapped[str | None] = mapped_column(Text, nullable=True)
    previous_key_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_key_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trust_status: Mapped[InstanceTrustStatus] = mapped_column(
        Enum(InstanceTrustStatus, name="instance_trust_status", create_constraint=True),
        default=InstanceTrustStatus.PENDING,
    )
    extra_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Part C — Trust Policies ──────────────────────────────


class TrustPolicy(Base):
    """Granular trust rules per peer per artifact type."""

    __tablename__ = "trust_policies"
    __table_args__ = (
        Index(
            "uq_trust_policy_instance_type",
            "instance_id",
            "artifact_type",
            "priority",
            unique=True,
        ),
        Index("ix_trust_policy_enabled", "enabled", postgresql_where="enabled = true"),
    )

    id: Mapped[str] = ulid_pk()
    instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    artifact_type: Mapped[TrustArtifactType] = mapped_column(
        Enum(TrustArtifactType, name="trust_artifact_type", create_constraint=True),
        nullable=False,
    )
    action: Mapped[TrustAction] = mapped_column(
        Enum(TrustAction, name="trust_action", create_constraint=True),
        nullable=False,
    )
    conditions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Part D — Federated Artifacts ─────────────────────────


class FederatedArtifact(Base):
    """A component (skill pack, workflow pack, etc.) discovered from a peer."""

    __tablename__ = "federated_artifacts"
    __table_args__ = (
        Index(
            "uq_fed_artifact_source",
            "source_instance_id",
            "source_artifact_id",
            "version",
            unique=True,
        ),
        Index("ix_fed_artifact_type", "artifact_type"),
        Index("ix_fed_artifact_category", "category"),
    )

    id: Mapped[str] = ulid_pk()
    source_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_artifact_id: Mapped[str] = mapped_column(String(26), nullable=False)
    artifact_type: Mapped[FederatedArtifactType] = mapped_column(
        Enum(FederatedArtifactType, name="federated_artifact_type", create_constraint=True),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    license_spdx: Mapped[str | None] = mapped_column(String(40), nullable=True)
    tags: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="[]")
    dependencies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    envelope_signature: Mapped[str] = mapped_column(Text, nullable=False)
    is_mirrored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mirror_status: Mapped[MirrorStatus | None] = mapped_column(
        Enum(MirrorStatus, name="mirror_status", create_constraint=True),
        nullable=True,
    )
    remote_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    extra_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )


# ── Part E — Credential Verification ────────────────────


class FederatedCredentialVerification(Base):
    """Record of a cross-instance credential verification."""

    __tablename__ = "federated_credential_verifications"
    __table_args__ = (
        Index("ix_fed_cred_verifier", "verifier_user_id"),
        Index("ix_fed_cred_source", "source_instance_id"),
        Index("ix_fed_cred_holder", "holder_pseudonym_id"),
        Index("ix_fed_cred_status", "verification_status"),
    )

    id: Mapped[str] = ulid_pk()
    verifier_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    verifier_org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    source_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    credential_type: Mapped[CredentialType] = mapped_column(
        Enum(CredentialType, name="credential_type", create_constraint=True),
        nullable=False,
    )
    holder_pseudonym_id: Mapped[str] = mapped_column(String(64), nullable=False)
    credential_envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    credential_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status", create_constraint=True),
        nullable=False,
    )
    verified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    revocation_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Part F — Account Linking & Portability ───────────────


class FederatedAccountLink(Base):
    """Explicit cross-instance account link for talent mobility."""

    __tablename__ = "federated_account_links"
    __table_args__ = (
        Index(
            "uq_account_link_user_instance",
            "local_user_id",
            "remote_instance_id",
            unique=True,
        ),
        Index("ix_account_link_status", "link_status"),
    )

    id: Mapped[str] = ulid_pk()
    local_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    remote_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    remote_pseudonym_id: Mapped[str] = mapped_column(String(64), nullable=False)
    link_status: Mapped[AccountLinkStatus] = mapped_column(
        Enum(AccountLinkStatus, name="account_link_status", create_constraint=True),
        default=AccountLinkStatus.PENDING,
    )
    linked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consent_scope: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PortabilityRecord(Base):
    """Tracks data exported across instances for a user."""

    __tablename__ = "portability_records"
    __table_args__ = (
        Index("ix_portability_user", "user_id"),
        Index("ix_portability_link", "account_link_id"),
    )

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_link_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federated_account_links.id", ondelete="CASCADE"),
        nullable=False,
    )
    record_type: Mapped[PortabilityRecordType] = mapped_column(
        Enum(PortabilityRecordType, name="portability_record_type", create_constraint=True),
        nullable=False,
    )
    data_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    exported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


# ── Part G — Federated Opportunities ────────────────────


class FederatedOpportunity(Base):
    """An employment/project opportunity from a peer instance."""

    __tablename__ = "federated_opportunities"
    __table_args__ = (
        Index(
            "uq_fed_opp_source",
            "source_instance_id",
            "source_opportunity_id",
            unique=True,
        ),
        Index("ix_fed_opp_status", "status"),
        Index(
            "ix_fed_opp_closes",
            "closes_at",
            postgresql_where="status = 'active'",
        ),
    )

    id: Mapped[str] = ulid_pk()
    source_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_opportunity_id: Mapped[str] = mapped_column(String(26), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    org_name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remote_ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    skills_required: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="[]")
    compensation_range: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    application_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    closes_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[OpportunityStatus] = mapped_column(
        Enum(OpportunityStatus, name="opportunity_status", create_constraint=True),
        default=OpportunityStatus.ACTIVE,
    )
    envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    envelope_signature: Mapped[str] = mapped_column(Text, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    extra_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default="{}"
    )


# ── Part H — Marketplace Federation ─────────────────────


class FederatedMarketplaceListing(Base):
    """A marketplace listing from a peer instance."""

    __tablename__ = "federated_marketplace_listings"
    __table_args__ = (
        Index(
            "uq_fed_listing_source",
            "source_instance_id",
            "source_listing_id",
            unique=True,
        ),
        Index("ix_fed_listing_type", "artifact_type"),
        Index(
            "ix_fed_listing_status",
            "status",
            postgresql_where="status = 'active'",
        ),
    )

    id: Mapped[str] = ulid_pk()
    source_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_listing_id: Mapped[str] = mapped_column(String(26), nullable=False)
    artifact_type: Mapped[FederatedArtifactType] = mapped_column(
        Enum(
            FederatedArtifactType,
            name="federated_artifact_type",
            create_constraint=True,
            create_type=False,
        ),
        nullable=False,
    )
    artifact_id: Mapped[str] = mapped_column(String(26), nullable=False)
    price_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    license_type: Mapped[str] = mapped_column(String(50), nullable=False)
    publisher_name: Mapped[str] = mapped_column(String(200), nullable=False)
    listing_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status", create_constraint=True),
        default=ListingStatus.ACTIVE,
    )
    envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class FederatedEntitlementGrant(Base):
    """License entitlement acquired from a peer marketplace."""

    __tablename__ = "federated_entitlement_grants"
    __table_args__ = (
        Index("ix_fed_entitlement_buyer", "buyer_org_id"),
        Index("ix_fed_entitlement_status", "grant_status"),
    )

    id: Mapped[str] = ulid_pk()
    listing_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federated_marketplace_listings.id", ondelete="CASCADE"),
        nullable=False,
    )
    buyer_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    buyer_user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    seller_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    grant_envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    grant_status: Mapped[EntitlementGrantStatus] = mapped_column(
        Enum(EntitlementGrantStatus, name="entitlement_grant_status", create_constraint=True),
        default=EntitlementGrantStatus.PENDING,
    )
    settlement_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    settlement_status: Mapped[SettlementStatus] = mapped_column(
        Enum(SettlementStatus, name="settlement_status", create_constraint=True),
        default=SettlementStatus.PENDING,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Part I — Ecosystem Intelligence Federation ──────────


class FederatedEcosystemObservation(Base):
    """An ecosystem intelligence observation from a peer."""

    __tablename__ = "federated_ecosystem_observations"
    __table_args__ = (
        Index(
            "uq_fed_eco_source",
            "source_instance_id",
            "source_observation_id",
            unique=True,
        ),
        Index("ix_fed_eco_type", "observation_type"),
        Index("ix_fed_eco_category", "category"),
    )

    id: Mapped[str] = ulid_pk()
    source_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_observation_id: Mapped[str] = mapped_column(String(26), nullable=False)
    observation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    observation_period: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    methodology: Mapped[str | None] = mapped_column(String(200), nullable=True)
    confidence: Mapped[float] = mapped_column(
        Float,
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="ck_eco_confidence"),
        nullable=False,
    )
    envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    status: Mapped[ObservationStatus] = mapped_column(
        Enum(ObservationStatus, name="observation_status", create_constraint=True),
        default=ObservationStatus.ACTIVE,
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Part K — Cross-instance Collaboration ───────────────


class FederationGrant(Base):
    """Scoped access grant for a remote user to participate locally."""

    __tablename__ = "federation_grants"
    __table_args__ = (
        Index("ix_fed_grant_org", "grantor_org_id"),
        Index("ix_fed_grant_grantee", "grantee_instance_id", "grantee_pseudonym_id"),
        Index("ix_fed_grant_resource", "resource_type", "resource_id"),
        Index(
            "ix_fed_grant_status",
            "status",
            postgresql_where="status = 'active'",
        ),
    )

    id: Mapped[str] = ulid_pk()
    grantor_org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    grantee_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    grantee_pseudonym_id: Mapped[str] = mapped_column(String(64), nullable=False)
    grant_type: Mapped[FederationGrantType] = mapped_column(
        Enum(FederationGrantType, name="federation_grant_type", create_constraint=True),
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(26), nullable=False)
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    status: Mapped[FederationGrantStatus] = mapped_column(
        Enum(FederationGrantStatus, name="federation_grant_status", create_constraint=True),
        default=FederationGrantStatus.PENDING,
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Part L — Revocation ─────────────────────────────────


class FederationRevocation(Base):
    """Signed revocation record from a peer (or self)."""

    __tablename__ = "federation_revocations"
    __table_args__ = (
        Index(
            "uq_fed_revocation_target",
            "target_type",
            "target_id",
            "instance_id",
            unique=True,
        ),
        Index(
            "ix_fed_revocation_unprocessed",
            "processed",
            postgresql_where="processed = false",
        ),
    )

    id: Mapped[str] = ulid_pk()
    instance_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    revocation_type: Mapped[RevocationType] = mapped_column(
        Enum(RevocationType, name="revocation_type", create_constraint=True),
        nullable=False,
    )
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    envelope_id: Mapped[str] = mapped_column(String(26), nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ── Part M — Data Residency ─────────────────────────────


class DataResidencyPolicy(Base):
    """Data residency / sovereignty rules for federation exchanges."""

    __tablename__ = "data_residency_policies"
    __table_args__ = (
        Index("ix_residency_org", "org_id"),
        Index(
            "ix_residency_enabled",
            "enabled",
            postgresql_where="enabled = true",
        ),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    policy_type: Mapped[ResidencyPolicyType] = mapped_column(
        Enum(ResidencyPolicyType, name="residency_policy_type", create_constraint=True),
        nullable=False,
    )
    artifact_types: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default='["all"]')
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    enforcement: Mapped[ResidencyEnforcement] = mapped_column(
        Enum(ResidencyEnforcement, name="residency_enforcement", create_constraint=True),
        default=ResidencyEnforcement.BLOCK,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Part N — Peer Reputation & Incidents ────────────────


class PeerReputationScore(Base):
    """Rolling reputation metrics for a federation peer."""

    __tablename__ = "peer_reputation_scores"

    instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        primary_key=True,
    )
    total_envelopes_received: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    invalid_signatures: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    expired_envelopes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    revocations_issued: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    policy_violations: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    spam_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_incident_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    auto_suspended: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PeerIncident(Base):
    """Individual trust incident for a federation peer."""

    __tablename__ = "peer_incidents"
    __table_args__ = (
        Index("ix_peer_incident_instance", "instance_id"),
        Index("ix_peer_incident_type", "incident_type"),
        Index(
            "ix_peer_incident_unresolved",
            "resolved_at",
            postgresql_where="resolved_at IS NULL",
        ),
    )

    id: Mapped[str] = ulid_pk()
    instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    incident_type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, name="incident_type", create_constraint=True),
        nullable=False,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity", create_constraint=True),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    envelope_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


# ── Part J — Federated Search ───────────────────────────


class FederationSearchCache(Base):
    """Cache for remote search results."""

    __tablename__ = "federation_search_cache"

    id: Mapped[str] = ulid_pk()
    query_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    results: Mapped[dict] = mapped_column(JSONB, nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FederationCircuitBreaker(Base):
    """Circuit breaker state per federation peer."""

    __tablename__ = "federation_circuit_breakers"

    instance_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("federation_instances.id", ondelete="CASCADE"),
        primary_key=True,
    )
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_failure_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    half_open_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
