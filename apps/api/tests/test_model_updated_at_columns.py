"""Models with updated_at should have server-side default."""

import pytest
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
)

MODELS_WITH_UPDATED = [DeveloperAccount, DeveloperApp, AppInstallation]

@pytest.mark.parametrize("model", MODELS_WITH_UPDATED, ids=lambda m: m.__name__)
def test_has_updated_at(model):
    cols = {c.name for c in model.__table__.columns}
    assert "updated_at" in cols

@pytest.mark.parametrize("model", MODELS_WITH_UPDATED, ids=lambda m: m.__name__)
def test_updated_at_nullable_or_default(model):
    col = model.__table__.columns["updated_at"]
    assert col.nullable or col.server_default is not None or col.default is not None
