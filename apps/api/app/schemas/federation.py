"""Federation API schemas — request/response models for cross-instance networking (ADR-017)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_header_str

# ── Shared validators ────────────────────────────────────


def _validate_uri(v: str) -> str:
    v = v.strip()
    if not v.startswith("https://"):
        raise ValueError("instance_uri must start with https://")
    if len(v) > 500:
        raise ValueError("instance_uri must not exceed 500 characters")
    return v.rstrip("/")


def _validate_short_str(v: str | None, field: str, limit: int) -> str | None:
    if v is not None:
        v = v.strip()
        if len(v) > limit:
            raise ValueError(f"{field} must not exceed {limit} characters")
        v = reject_header_str(v, field)
    return v


# ── Instance Identity ────────────────────────────────────


class InstanceIdentityResponse(BaseModel):
    instance_uri: str
    display_name: str
    public_key_pem: str
    key_id: str
    protocol_version: str
    metadata: dict


class UpdateInstanceIdentityRequest(BaseModel):
    display_name: str | None = None
    metadata: dict | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        return _validate_short_str(v, "display_name", 200)


class WellKnownFederationResponse(BaseModel):
    instance_uri: str
    display_name: str
    public_key_pem: str
    key_id: str
    protocol_version: str
    software_version: str
    metadata: dict
    supported_artifact_types: list[str]
    federation_endpoints: dict[str, str]


# ── Peer Management ──────────────────────────────────────


class AddPeerRequest(BaseModel):
    instance_uri: str

    @field_validator("instance_uri")
    @classmethod
    def validate_instance_uri(cls, v: str) -> str:
        return _validate_uri(v)


class PeerReputationSummary(BaseModel):
    total_envelopes: int = 0
    invalid_signature_rate: float = 0.0
    spam_score: float = 0.0


class PeerResponse(BaseModel):
    id: str
    instance_uri: str
    display_name: str
    description: str | None = None
    logo_url: str | None = None
    software_version: str | None = None
    protocol_version: str
    key_id: str
    trust_status: str
    last_seen_at: datetime | None = None
    last_sync_error: str | None = None
    reputation: PeerReputationSummary | None = None
    created_at: datetime
    updated_at: datetime


class UpdatePeerRequest(BaseModel):
    trust_status: str | None = None
    display_name: str | None = None
    description: str | None = None

    @field_validator("trust_status")
    @classmethod
    def validate_trust_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("pending", "trusted", "suspended", "revoked"):
            raise ValueError("trust_status must be one of: pending, trusted, suspended, revoked")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        return _validate_short_str(v, "display_name", 200)


# ── Trust Policies ───────────────────────────────────────


class CreateTrustPolicyRequest(BaseModel):
    artifact_type: str
    action: str
    conditions: dict | None = None
    priority: int = Field(default=0, ge=0, le=1000)
    enabled: bool = True

    @field_validator("artifact_type")
    @classmethod
    def validate_artifact_type(cls, v: str) -> str:
        valid = {
            "registry_artifact", "credential", "opportunity",
            "marketplace_listing", "ecosystem_observation", "all",
        }
        if v not in valid:
            raise ValueError(f"artifact_type must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("accept", "mirror", "reject"):
            raise ValueError("action must be one of: accept, mirror, reject")
        return v


class UpdateTrustPolicyRequest(BaseModel):
    action: str | None = None
    conditions: dict | None = None
    priority: int | None = Field(default=None, ge=0, le=1000)
    enabled: bool | None = None

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str | None) -> str | None:
        if v is not None and v not in ("accept", "mirror", "reject"):
            raise ValueError("action must be one of: accept, mirror, reject")
        return v


class TrustPolicyResponse(BaseModel):
    id: str
    instance_id: str
    artifact_type: str
    action: str
    conditions: dict | None = None
    priority: int
    enabled: bool
    created_at: datetime
    updated_at: datetime


# ── Federated Artifacts ──────────────────────────────────


class FederatedArtifactResponse(BaseModel):
    id: str
    source_instance: str | None = None  # enriched from instance_uri
    source_instance_id: str
    source_artifact_id: str
    artifact_type: str
    name: str
    version: str
    description: str | None = None
    content_hash: str
    category: str | None = None
    author_name: str | None = None
    license_spdx: str | None = None
    tags: list = []
    is_mirrored: bool
    mirror_status: str | None = None
    remote_deleted: bool
    first_seen_at: datetime
    last_synced_at: datetime


# ── Credential Verification ─────────────────────────────


class VerifyCredentialRequest(BaseModel):
    """Submit a signed credential envelope for verification."""
    envelope: dict  # full signed envelope


class CredentialVerificationResponse(BaseModel):
    id: str
    credential_type: str
    holder_pseudonym_id: str
    verification_status: str
    credential_data: dict
    verified_at: datetime
    source_instance: str | None = None


# ── Federated Opportunities ─────────────────────────────


class FederatedOpportunityResponse(BaseModel):
    id: str
    source_instance: str | None = None
    source_instance_id: str
    source_opportunity_id: str
    title: str
    description: str | None = None
    org_name: str
    location: str | None = None
    remote_ok: bool
    skills_required: list = []
    compensation_range: dict | None = None
    application_url: str | None = None
    closes_at: datetime | None = None
    status: str
    first_seen_at: datetime


# ── Federated Search ─────────────────────────────────────


class FederatedSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    types: list[str] | None = None
    include_remote: bool = True
    max_peers: int = Field(default=5, ge=1, le=20)
    timeout_ms: int = Field(default=3000, ge=500, le=30000)


class FederatedSearchResponse(BaseModel):
    local_results: list[dict]
    remote_results: list[dict]
    meta: dict


# ── Revocations ──────────────────────────────────────────


class RevocationResponse(BaseModel):
    id: str
    instance_id: str | None = None
    revocation_type: str
    target_type: str
    target_id: str
    reason: str | None = None
    revoked_at: datetime
    processed: bool
    processed_at: datetime | None = None


# ── Data Residency ───────────────────────────────────────


class CreateResidencyPolicyRequest(BaseModel):
    org_id: str | None = None
    policy_type: str
    artifact_types: list[str] = Field(default_factory=lambda: ["all"])
    conditions: dict
    enforcement: str = "block"
    enabled: bool = True

    @field_validator("policy_type")
    @classmethod
    def validate_policy_type(cls, v: str) -> str:
        valid = {"region_restrict", "jurisdiction_restrict", "retention_limit", "cross_border_block"}
        if v not in valid:
            raise ValueError(f"policy_type must be one of: {', '.join(sorted(valid))}")
        return v

    @field_validator("enforcement")
    @classmethod
    def validate_enforcement(cls, v: str) -> str:
        if v not in ("block", "warn", "audit_only"):
            raise ValueError("enforcement must be one of: block, warn, audit_only")
        return v


class ResidencyPolicyResponse(BaseModel):
    id: str
    org_id: str | None = None
    policy_type: str
    artifact_types: list
    conditions: dict
    enforcement: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


# ── Sync Status ──────────────────────────────────────────


class SyncStatusResponse(BaseModel):
    total_peers: int
    trusted_peers: int
    total_artifacts: int
    total_credentials_verified: int
    total_opportunities: int
    last_sync_at: datetime | None = None


# ── Incidents ────────────────────────────────────────────


class PeerIncidentResponse(BaseModel):
    id: str
    instance_id: str
    incident_type: str
    severity: str
    description: str | None = None
    envelope_id: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None
    resolved_by: str | None = None


class ResolveIncidentRequest(BaseModel):
    resolved: bool = True


# ── Envelope ─────────────────────────────────────────────


class SignedEnvelope(BaseModel):
    """The wire format for federation messages."""
    envelope_version: str = "1.0"
    envelope_id: str
    envelope_type: str
    source_instance: str
    source_key_id: str
    issued_at: datetime
    expires_at: datetime | None = None
    payload: dict
    signature: str
