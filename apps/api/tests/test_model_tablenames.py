"""Parametrized tests for all developer platform model tablenames."""

import pytest
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
)
from app.models.webhook_delivery import AppWebhookDelivery

MODELS = [
    (DeveloperAccount, "developer_accounts"),
    (DeveloperApp, "developer_apps"),
    (AppVersion, "app_versions"),
    (AppInstallation, "app_installations"),
    (AppApiKey, "app_api_keys"),
    (AppEventSubscription, "app_event_subscriptions"),
    (AppAutomationRule, "app_automation_rules"),
    (AppSecret, "app_secrets"),
    (AppUiExtension, "app_ui_extensions"),
    (SandboxExecution, "sandbox_executions"),
    (AppReviewSubmission, "app_review_submissions"),
    (AppSigningKey, "app_signing_keys"),
    (AppWebhookDelivery, "app_webhook_deliveries"),
]

@pytest.mark.parametrize("model,table", MODELS, ids=lambda m: m.__name__ if hasattr(m, '__name__') else str(m))
def test_tablename(model, table):
    assert model.__tablename__ == table

@pytest.mark.parametrize("model,table", MODELS, ids=lambda m: m.__name__ if hasattr(m, '__name__') else str(m))
def test_has_id(model, table):
    assert hasattr(model, "id")

@pytest.mark.parametrize("model,table", MODELS, ids=lambda m: m.__name__ if hasattr(m, '__name__') else str(m))
def test_has_timestamp(model, table):
    assert hasattr(model, "created_at") or hasattr(model, "submitted_at")

def test_total_models():
    assert len(MODELS) == 13
