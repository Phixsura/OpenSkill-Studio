"""Developer schema validation tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import (
    CreateDeveloperAccountRequest,
    CreateAppRequest,
    CreateAppVersionRequest,
    CreateApiKeyRequest,
    CreateEventSubscriptionRequest,
    CreateAutomationRuleRequest,
)

# --- CreateDeveloperAccountRequest ---

def test_create_dev_account_valid():
    r = CreateDeveloperAccountRequest(display_name="My Studio", slug="my-studio", support_email="dev@example.com")
    assert r.display_name == "My Studio"

INVALID_DEV_ACCOUNTS = [
    ({"display_name": "", "slug": "s", "support_email": "a@b.c"}, "empty name"),
    ({"display_name": "X", "slug": "", "support_email": "a@b.c"}, "empty slug"),
    ({"display_name": "X", "slug": "s"}, "missing email"),
]

@pytest.mark.parametrize("data,desc", INVALID_DEV_ACCOUNTS, ids=lambda x: str(x)[:30])
def test_create_dev_account_invalid(data, desc):
    with pytest.raises(ValidationError):
        CreateDeveloperAccountRequest(**data)

# --- CreateAppRequest ---

def test_create_app_valid():
    r = CreateAppRequest(name="Test App", slug="test-app", category="automation")
    assert r.slug == "test-app"

INVALID_APPS = [
    ({"name": "", "slug": "s", "category": "automation"}, "empty name"),
    ({"name": "X", "slug": "s", "category": "INVALID_CAT"}, "bad category"),
]

@pytest.mark.parametrize("data,desc", INVALID_APPS, ids=lambda x: str(x)[:30])
def test_create_app_invalid(data, desc):
    with pytest.raises(ValidationError):
        CreateAppRequest(**data)

# --- CreateApiKeyRequest ---

def test_create_api_key_valid():
    r = CreateApiKeyRequest(name="prod-key")
    assert r.name == "prod-key"

def test_create_api_key_empty_name():
    with pytest.raises(ValidationError):
        CreateApiKeyRequest(name="")

# --- CreateEventSubscriptionRequest ---

def test_create_event_sub_valid():
    r = CreateEventSubscriptionRequest(event_type="submission.completed")
    assert r.event_type == "submission.completed"

# --- CreateAutomationRuleRequest ---

def test_create_rule_valid():
    r = CreateAutomationRuleRequest(
        name="Auto grade",
        trigger_event="submission.completed",
        action_type="webhook",
        action_config={"url": "https://example.com/hook"},
    )
    assert r.name == "Auto grade"
