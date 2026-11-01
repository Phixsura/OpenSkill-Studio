"""Model tablename convention — all tables should be snake_case plural."""

import pytest
import re
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
)
from app.models.webhook_delivery import AppWebhookDelivery

ALL_MODELS = [
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
    AppWebhookDelivery,
]

@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_tablename_snake_case(model):
    assert re.match(r'^[a-z][a-z0-9_]+$', model.__tablename__), \
        f"{model.__name__} tablename '{model.__tablename__}' not snake_case"

@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_tablename_plural(model):
    name = model.__tablename__
    assert name.endswith('s'), f"{model.__name__} tablename '{name}' should be plural"

@pytest.mark.parametrize("model", ALL_MODELS, ids=lambda m: m.__name__)
def test_tablename_no_camelcase(model):
    assert model.__tablename__ == model.__tablename__.lower()
