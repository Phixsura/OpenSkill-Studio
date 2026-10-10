"""Integration fabric API schemas (ADR-018 §15).

All inbound models are extra="forbid" (R85). Credential responses carry
exactly {id, kind, expires_at, rotated_at} — never ciphertext or token
material; the response-model allowlist test enforces this structurally.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ── Providers (catalog, read-only) ──


class ProviderResponse(BaseModel):
    id: str
    key: str
    category: str
    auth_mode: str
    display_name: str
    capabilities: list[str]
    config_schema: dict
    version: int
    enabled: bool


# ── Connections ──


class ConnectionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_key: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    config: dict = Field(default_factory=dict)
    base_url: str | None = Field(default=None, max_length=500)


class ConnectionUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    config: dict | None = None
    base_url: str | None = Field(default=None, max_length=500)
    # Admin toggle: only "disabled" or "pending" (re-enable) accepted here;
    # other statuses are machine-managed (§4.2 state machine).
    status: str | None = None


class ConnectionResponse(BaseModel):
    id: str
    org_id: str
    provider_key: str
    provider_version: int
    name: str
    status: str
    config: dict
    base_url: str | None
    health: dict
    has_credential: bool
    created_at: datetime
    updated_at: datetime


# ── Credentials (write-only) ──


class CredentialWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str
    # {field_name: value} — encrypted as one envelope; individual values
    # capped to keep the ciphertext bounded.
    values: dict[str, str] = Field(min_length=1, max_length=20)
    expires_at: datetime | None = None


class CredentialResponse(BaseModel):
    """The ONLY shape credential data ever leaves the API in."""

    id: str
    kind: str
    expires_at: datetime | None
    rotated_at: datetime


class PingResponse(BaseModel):
    ok: bool
    status: str
    detail: str | None = None
