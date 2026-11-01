"""Model relationship / foreign key tests."""

import pytest
from sqlalchemy import inspect as sa_inspect
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
)

FK_CASES = [
    (DeveloperApp, "developer_id", "developer_accounts.id"),
    (AppVersion, "app_id", "developer_apps.id"),
    (AppInstallation, "app_id", "developer_apps.id"),
    (AppApiKey, "app_id", "developer_apps.id"),
    (AppEventSubscription, "installation_id", "app_installations.id"),
    (AppAutomationRule, "installation_id", "app_installations.id"),
    (AppSecret, "installation_id", "app_installations.id"),
    (AppUiExtension, "app_id", "developer_apps.id"),
    (SandboxExecution, "installation_id", "app_installations.id"),
    (AppReviewSubmission, "app_id", "developer_apps.id"),
    (AppSigningKey, "developer_id", "developer_accounts.id"),
]

@pytest.mark.parametrize("model,fk_col,target", FK_CASES,
    ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x)[:30])
def test_foreign_key_exists(model, fk_col, target):
    col = model.__table__.columns[fk_col]
    fk_targets = [str(fk.target_fullname) for fk in col.foreign_keys]
    assert target in fk_targets, f"{model.__name__}.{fk_col} FK should point to {target}, got {fk_targets}"
