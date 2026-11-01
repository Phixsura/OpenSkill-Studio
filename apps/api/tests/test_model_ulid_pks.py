"""All developer models use ULID-style string primary keys."""

import pytest
from sqlalchemy import String
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
)
from app.models.webhook_delivery import AppWebhookDelivery

MODELS = [
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppEventSubscription, AppAutomationRule, AppSecret,
    AppUiExtension, SandboxExecution, AppReviewSubmission, AppSigningKey,
    AppWebhookDelivery,
]

@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_pk_is_string_type(model):
    id_col = model.__table__.columns["id"]
    assert isinstance(id_col.type, String) or "char" in str(id_col.type).lower() or "text" in str(id_col.type).lower()

@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_pk_is_primary(model):
    id_col = model.__table__.columns["id"]
    assert id_col.primary_key

@pytest.mark.parametrize("model", MODELS, ids=lambda m: m.__name__)
def test_pk_not_nullable(model):
    id_col = model.__table__.columns["id"]
    assert not id_col.nullable
