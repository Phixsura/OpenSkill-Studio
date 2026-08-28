"""Schemas for capability taxonomy and provider four-entity model (ADR-011)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.base import (
    reject_ctrl_json,
    reject_ctrl_str,
    reject_deep_json,
    reject_nonfinite_json,
)

# ── Capability ────────────────────────────────────────────


class CapabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    name: str
    description: str | None = None
    category: str
    contract_version: int
    io_signature: dict
    is_platform: bool


# ── Adapter (platform catalog, read-only) ─────────────────


class AdapterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    name: str
    description: str | None = None
    config_schema: dict
    credential_fields: list  # field NAMES only — never values
    is_active: bool


# ── Connection ────────────────────────────────────────────


class CreateConnectionRequest(BaseModel):
    adapter_id: str
    name: str
    config: dict = {}
    # Credential values are write-only: accepted here, encrypted at rest,
    # never returned by any endpoint.
    credentials: dict[str, str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return reject_ctrl_str(v, "name")

    @field_validator("config")
    @classmethod
    def validate_config_size(cls, v: dict) -> dict:
        if len(str(v)) > 10000:
            raise ValueError("Config too large (max 10,000 chars)")
        reject_deep_json(v, "config")
        reject_nonfinite_json(v, "config")
        return reject_ctrl_json(v, "config")

    @field_validator("credentials")
    @classmethod
    def validate_credentials(cls, v: dict | None) -> dict | None:
        if v is not None:
            if len(v) > 10:
                raise ValueError("Too many credential fields")
            for key, val in v.items():
                if len(key) > 64 or len(val) > 2000:
                    raise ValueError("Credential field too large")
        return v


class UpdateConnectionRequest(BaseModel):
    name: str | None = None
    config: dict | None = None
    credentials: dict[str, str] | None = None
    status: str | None = None

    # None-tolerant mirror of the create-request validator — updates must
    # not bypass the bounds enforced at creation time
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v or len(v) > 100:
            raise ValueError("Name must be 1-100 characters")
        return reject_ctrl_str(v, "name")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("active", "disabled"):
            raise ValueError("Status must be active or disabled")
        return v

    @field_validator("config")
    @classmethod
    def validate_config_size(cls, v: dict | None) -> dict | None:
        if v is not None and len(str(v)) > 10000:
            raise ValueError("Config too large (max 10,000 chars)")
        reject_deep_json(v, "config")
        reject_nonfinite_json(v, "config")
        return reject_ctrl_json(v, "config")

    @field_validator("credentials")
    @classmethod
    def validate_credentials(cls, v: dict | None) -> dict | None:
        if v is not None:
            if len(v) > 10:
                raise ValueError("Too many credential fields")
            for key, val in v.items():
                if len(key) > 64 or len(val) > 2000:
                    raise ValueError("Credential field too large")
        return v


class ConnectionResponse(BaseModel):
    """Connection response — NEVER includes credential values."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    adapter_id: str
    name: str
    config: dict
    credential_id: str | None = None  # reference only
    status: str
    last_health_at: datetime | None = None
    health_status: str | None = None
    created_at: datetime


# ── Offering ──────────────────────────────────────────────


class CreateOfferingRequest(BaseModel):
    connection_id: str
    capability_key: str
    model_name: str
    features: list[str] = []
    limits: dict = {}
    cost_per_call_usd: float | None = None
    quality_tier: str = "standard"

    @field_validator("capability_key")
    @classmethod
    def validate_capability_key(cls, v: str) -> str:
        if not v or len(v) > 64:
            raise ValueError("Capability key must be 1-64 characters")
        return v

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 200:
            raise ValueError("Model name must be 1-200 characters")
        return reject_ctrl_str(v, "model_name")

    @field_validator("quality_tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        if v not in ("draft", "standard", "premium"):
            raise ValueError("Quality tier must be draft, standard, or premium")
        return v

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: list) -> list:
        if len(v) > 20:
            raise ValueError("Too many features (max 20)")
        for f in v:
            if not isinstance(f, str) or len(f) > 64:
                raise ValueError("Feature entries must be strings of max 64 chars")
            reject_ctrl_str(f, "features")
        return v

    @field_validator("limits")
    @classmethod
    def validate_limits_size(cls, v: dict) -> dict:
        if len(str(v)) > 5000:
            raise ValueError("Limits too large (max 5,000 chars)")
        reject_deep_json(v, "limits")
        reject_nonfinite_json(v, "limits")
        return reject_ctrl_json(v, "limits")

    @field_validator("cost_per_call_usd")
    @classmethod
    def validate_cost(cls, v: float | None) -> float | None:
        # Numeric(10, 6) tops out at 9999.999999, and Postgres ROUNDS to
        # 6 fraction digits at insert — so [9999.9999995, 10000) rounds to
        # 10000.000000 and still overflows. Bound the ROUNDED value. NaN
        # (which compares False everywhere and later crashes Decimal sorts)
        # and infinities are rejected by the same round() guard.
        if v is not None:
            import math

            if not math.isfinite(v):
                raise ValueError("Cost must be a finite number")
            if v < 0 or round(v, 6) >= 10000:
                raise ValueError("Cost must be between 0 and 9,999.999999")
        return v


class UpdateOfferingRequest(BaseModel):
    model_name: str | None = None
    features: list[str] | None = None
    limits: dict | None = None
    cost_per_call_usd: float | None = None
    quality_tier: str | None = None
    is_active: bool | None = None

    @field_validator("quality_tier")
    @classmethod
    def validate_tier(cls, v: str | None) -> str | None:
        if v is not None and v not in ("draft", "standard", "premium"):
            raise ValueError("Quality tier must be draft, standard, or premium")
        return v

    # None-tolerant mirrors of the create-request validators — updates must
    # not bypass the bounds enforced at creation time
    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v or len(v) > 200:
            raise ValueError("Model name must be 1-200 characters")
        return reject_ctrl_str(v, "model_name")

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: list | None) -> list | None:
        if v is None:
            return v
        if len(v) > 20:
            raise ValueError("Too many features (max 20)")
        for f in v:
            if not isinstance(f, str) or len(f) > 64:
                raise ValueError("Feature entries must be strings of max 64 chars")
            reject_ctrl_str(f, "features")
        return v

    @field_validator("limits")
    @classmethod
    def validate_limits_size(cls, v: dict | None) -> dict | None:
        if v is not None and len(str(v)) > 5000:
            raise ValueError("Limits too large (max 5,000 chars)")
        reject_deep_json(v, "limits")
        reject_nonfinite_json(v, "limits")
        return reject_ctrl_json(v, "limits")

    @field_validator("cost_per_call_usd")
    @classmethod
    def validate_cost(cls, v: float | None) -> float | None:
        # Numeric(10, 6) tops out at 9999.999999, and Postgres ROUNDS to
        # 6 fraction digits at insert — so [9999.9999995, 10000) rounds to
        # 10000.000000 and still overflows. Bound the ROUNDED value. NaN
        # (which compares False everywhere and later crashes Decimal sorts)
        # and infinities are rejected by the same round() guard.
        if v is not None:
            import math

            if not math.isfinite(v):
                raise ValueError("Cost must be a finite number")
            if v < 0 or round(v, 6) >= 10000:
                raise ValueError("Cost must be between 0 and 9,999.999999")
        return v


class OfferingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    connection_id: str
    capability_key: str
    model_name: str
    features: list
    limits: dict
    cost_per_call_usd: float | None = None
    quality_tier: str
    is_active: bool
    created_at: datetime
