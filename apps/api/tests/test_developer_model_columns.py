"""Verify all developer model columns exist."""

import pytest
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
)

MODELS_AND_REQUIRED_COLS = [
    (DeveloperAccount, {"id", "owner_user_id", "display_name", "slug", "support_email", "status"}),
    (DeveloperApp, {"id", "developer_id", "name", "slug", "category", "status", "oauth_client_id"}),
    (AppVersion, {"id", "app_id", "version", "manifest", "content_hash", "review_status"}),
    (AppInstallation, {"id", "app_id", "app_version_id", "org_id", "installed_by", "status"}),
    (AppApiKey, {"id", "app_id", "name", "key_prefix", "key_hash"}),
    (AppEventSubscription, {"id", "installation_id", "event_type", "enabled"}),
    (AppAutomationRule, {"id", "installation_id", "name", "trigger_event", "action_type", "action_config"}),
    (AppSecret, {"id", "installation_id", "key", "encrypted_value"}),
    (AppUiExtension, {"id", "app_id", "surface", "title", "entry_path"}),
    (SandboxExecution, {"id", "installation_id", "function_name", "status"}),
    (AppReviewSubmission, {"id", "app_id", "app_version_id", "submitted_by", "review_status"}),
    (AppSigningKey, {"id", "developer_id", "public_key", "fingerprint", "name"}),
]

@pytest.mark.parametrize("model,required_cols", MODELS_AND_REQUIRED_COLS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_required_columns(model, required_cols):
    actual = {c.name for c in model.__table__.columns}
    missing = required_cols - actual
    assert missing == set(), f"{model.__name__} missing columns: {missing}"
