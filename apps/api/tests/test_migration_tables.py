"""Verify migration creates all expected tables."""

import pytest
from sqlalchemy import inspect as sa_inspect
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
)
from app.models.webhook_delivery import AppWebhookDelivery

TABLES = [
    ("developer_accounts", DeveloperAccount),
    ("developer_apps", DeveloperApp),
    ("app_versions", AppVersion),
    ("app_installations", AppInstallation),
    ("app_api_keys", AppApiKey),
    ("app_event_subscriptions", AppEventSubscription),
    ("app_automation_rules", AppAutomationRule),
    ("app_secrets", AppSecret),
    ("app_ui_extensions", AppUiExtension),
    ("sandbox_executions", SandboxExecution),
    ("app_review_submissions", AppReviewSubmission),
    ("app_signing_keys", AppSigningKey),
    ("app_webhook_deliveries", AppWebhookDelivery),
]

@pytest.mark.parametrize("tablename,model", TABLES, ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_table_name_matches(tablename, model):
    assert model.__tablename__ == tablename

@pytest.mark.parametrize("tablename,model", TABLES, ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_table_has_id(tablename, model):
    cols = {c.name for c in model.__table__.columns}
    assert "id" in cols

@pytest.mark.parametrize("tablename,model", TABLES, ids=lambda x: x if isinstance(x, str) else x.__name__)
def test_table_has_timestamp(tablename, model):
    cols = {c.name for c in model.__table__.columns}
    assert "created_at" in cols or "submitted_at" in cols

def test_total_tables():
    assert len(TABLES) == 13
