"""Plan / entitlement schemas (ADR-014 §2)."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import reject_ctrl_str, reject_deep_json


class CreatePlanRequest(BaseModel):
    key: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name", "description")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class PlanPriceInput(BaseModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    interval: str = Field(pattern=r"^(month|year)$")
    amount_minor: int = Field(ge=0, le=10_000_000_000)
    included_seats: int = Field(default=0, ge=0, le=1_000_000)
    overage_seat_amount_minor: int | None = Field(default=None, ge=0, le=10_000_000)


class UpdateDraftVersionRequest(BaseModel):
    entitlements: dict | None = None
    prices: list[PlanPriceInput] | None = Field(default=None, max_length=20)

    @field_validator("entitlements")
    @classmethod
    def _depth(cls, v):
        return reject_deep_json(v, "entitlements", limit=4)


class SetExternalRefRequest(BaseModel):
    """R62[2]: backfill the provider price id (the one ADR-noted mutable
    field on an active version). None clears it."""

    external_price_ref: str | None = Field(default=None, max_length=100)


class SetOverrideRequest(BaseModel):
    value: bool | int | str | None
    enforcement: str = Field(default="hard", pattern=r"^(hard|soft)$")
    expires_at: datetime | None = None
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def _ctrl(cls, v, info):
        return reject_ctrl_str(v, info.field_name)


class PlanPriceResponse(BaseModel):
    id: str
    currency: str
    interval: str
    amount_minor: int
    included_seats: int
    overage_seat_amount_minor: int | None
    external_price_ref: str | None

    model_config = {"from_attributes": True}


class PlanVersionResponse(BaseModel):
    id: str
    plan_id: str
    version: int
    status: str
    entitlements: dict
    activated_at: datetime | None
    created_at: datetime
    prices: list[PlanPriceResponse] = []

    model_config = {"from_attributes": True}


class PlanResponse(BaseModel):
    id: str
    key: str
    name: str
    description: str | None
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}
