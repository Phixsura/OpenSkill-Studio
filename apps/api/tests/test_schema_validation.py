"""Tests for Pydantic schema validation in developer schemas."""

import pytest
from app.schemas.developer import (
    CreateAppRequest, CreateAppVersionRequest, CreateDeveloperAccountRequest,
    CreateApiKeyRequest, CreateAutomationRuleRequest, CreateEventSubscriptionRequest,
    SetSecretRequest, InstallAppRequest,
)


def test_account_slug_lowercase():
    req = CreateDeveloperAccountRequest(display_name="Test", slug="MySlug", support_email="t@t.com")
    assert req.slug == "myslug"

def test_account_slug_strips():
    req = CreateDeveloperAccountRequest(display_name="Test", slug=" my-slug ", support_email="t@t.com")
    assert req.slug == "my-slug"

def test_account_email_lowercase():
    req = CreateDeveloperAccountRequest(display_name="Test", slug="test-slug", support_email="Test@Example.COM")
    assert req.support_email == "test@example.com"

def test_app_slug_validation():
    req = CreateAppRequest(name="Test", slug="valid-slug", category="connector")
    assert req.slug == "valid-slug"

def test_app_invalid_category():
    with pytest.raises(ValueError):
        CreateAppRequest(name="Test", slug="test", category="invalid")

def test_app_invalid_visibility():
    with pytest.raises(ValueError):
        CreateAppRequest(name="Test", slug="test", category="connector", visibility="secret")

def test_version_semver_valid():
    req = CreateAppVersionRequest(version="1.2.3", manifest={"schema_version": "1.0", "app": {}, "permissions": []}, content_hash="a" * 64)
    assert req.version == "1.2.3"

def test_version_semver_prerelease():
    req = CreateAppVersionRequest(version="1.0.0-beta.1", manifest={"schema_version": "1.0", "app": {}, "permissions": []}, content_hash="a" * 64)
    assert req.version == "1.0.0-beta.1"

def test_version_invalid_format():
    with pytest.raises(ValueError):
        CreateAppVersionRequest(version="1.0", manifest={}, content_hash="a" * 64)

def test_version_invalid_hash():
    with pytest.raises(ValueError):
        CreateAppVersionRequest(version="1.0.0", manifest={}, content_hash="short")

def test_api_key_name_required():
    req = CreateApiKeyRequest(name="My Key")
    assert req.name == "My Key"

def test_secret_key_uppercase():
    req = SetSecretRequest(key="my_key", value="secret")
    assert req.key == "MY_KEY"

def test_secret_key_invalid():
    with pytest.raises(ValueError):
        SetSecretRequest(key="lower-case!", value="v")

def test_event_subscription_type():
    req = CreateEventSubscriptionRequest(event_type="submission.completed")
    assert req.event_type == "submission.completed"

def test_automation_rule_invalid_action():
    with pytest.raises(ValueError):
        CreateAutomationRuleRequest(name="R", trigger_event="e", action_type="invalid", action_config={})

def test_install_app_defaults():
    req = InstallAppRequest(app_id="app-1")
    assert req.granted_permissions == []
    assert req.config == {}
    assert req.pinned_version is False
