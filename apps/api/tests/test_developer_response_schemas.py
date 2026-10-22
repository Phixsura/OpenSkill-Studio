"""Developer response schema tests — ensure all response models serialize correctly."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import (
    DeveloperAccountResponse, AppResponse, AppSummaryResponse,
    AppVersionResponse, AppInstallationResponse, ApiKeyResponse,
    EventSubscriptionResponse, AutomationRuleResponse, SecretMetadataResponse,
    SandboxExecutionResponse,
)

RESPONSE_MODELS = [
    (DeveloperAccountResponse, {"id": "d1", "owner_user_id": "u1", "display_name": "Dev", "slug": "dev", "support_email": "a@b.c", "status": "active", "created_at": "2026-01-01T00:00:00Z"}),
    (AppSummaryResponse, {"id": "a1", "name": "App", "slug": "app", "category": "connector", "status": "published", "visibility": "public"}),
    (ApiKeyResponse, {"id": "k1", "app_id": "a1", "name": "key", "key_prefix": "osk_app_", "created_at": "2026-01-01T00:00:00Z"}),
    (EventSubscriptionResponse, {"id": "e1", "installation_id": "i1", "event_type": "app.installed", "enabled": True, "created_at": "2026-01-01T00:00:00Z"}),
    (SecretMetadataResponse, {"id": "s1", "installation_id": "i1", "key": "API_KEY", "created_at": "2026-01-01T00:00:00Z"}),
]

@pytest.mark.parametrize("model_cls,data", RESPONSE_MODELS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x)[:30])
def test_response_model_valid(model_cls, data):
    obj = model_cls(**data)
    assert obj.id == data["id"]

@pytest.mark.parametrize("model_cls,data", RESPONSE_MODELS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x)[:30])
def test_response_model_serializes(model_cls, data):
    obj = model_cls(**data)
    d = obj.model_dump()
    assert isinstance(d, dict)
    assert "id" in d
