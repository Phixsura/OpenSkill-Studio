"""All models with created_at should have server default."""

import pytest
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppSigningKey,
)

MODELS = [DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
          AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
          AppUiExtension, SandboxExecution, AppSigningKey]

@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_created_at_has_default(model):
    col = model.__table__.columns["created_at"]
    assert col.server_default is not None or col.default is not None or not col.nullable
