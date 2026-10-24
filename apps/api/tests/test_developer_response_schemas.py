"""Developer response schema tests."""

import pytest
from app.schemas.developer import (
    DeveloperAccountResponse, AppSummaryResponse, ApiKeyResponse,
    EventSubscriptionResponse, SecretMetadataResponse,
)

NOW = "2026-01-01T00:00:00Z"

RESPONSE_MODELS = [
    (DeveloperAccountResponse, {"id": "d1", "owner_user_id": "u1", "org_id": "o1", "display_name": "Dev", "slug": "dev", "website_url": None, "support_email": "a@b.c", "verified": False, "status": "active", "created_at": NOW, "updated_at": NOW}),
    (AppSummaryResponse, {"id": "a1", "name": "App", "slug": "app", "description": None, "icon_url": None, "category": "connector", "status": "published", "visibility": "public"}),
    (ApiKeyResponse, {"id": "k1", "app_id": "a1", "installation_id": "i1", "name": "key", "key_prefix": "osk_app_", "scopes": ["read:cohorts"], "rate_limit_tier": "standard", "last_used_at": None, "expires_at": None, "created_at": NOW}),
    (EventSubscriptionResponse, {"id": "e1", "installation_id": "i1", "event_type": "app.installed", "enabled": True, "filter_expression": None, "created_at": NOW}),
    (SecretMetadataResponse, {"id": "s1", "installation_id": "i1", "key": "API_KEY", "description": None, "created_at": NOW, "updated_at": NOW}),
]

@pytest.mark.parametrize("cls,data", RESPONSE_MODELS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x)[:30])
def test_valid(cls, data):
    obj = cls(**data)
    assert obj.id == data["id"]

@pytest.mark.parametrize("cls,data", RESPONSE_MODELS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x)[:30])
def test_serializes(cls, data):
    d = cls(**data).model_dump()
    assert isinstance(d, dict) and "id" in d
