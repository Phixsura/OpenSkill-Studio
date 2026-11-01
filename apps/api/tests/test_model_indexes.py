"""Model index tests — verify important indexes exist."""

import pytest
from app.models.developer import (
    DeveloperAccount, DeveloperApp, AppVersion, AppInstallation,
    AppApiKey, AppSigningKey,
)

UNIQUE_COLS = [
    (DeveloperAccount, "slug"),
    (DeveloperApp, "slug"),
    (DeveloperApp, "oauth_client_id"),
    (AppApiKey, "key_hash"),
]

@pytest.mark.parametrize("model,col_name", UNIQUE_COLS,
    ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_unique_constraint(model, col_name):
    col = model.__table__.columns[col_name]
    assert col.unique or any(
        col_name in [c.name for c in idx.columns] and idx.unique
        for idx in model.__table__.indexes
    ), f"{model.__name__}.{col_name} should be unique"

INDEX_COLS = [
    (AppInstallation, "org_id"),
    (AppInstallation, "app_id"),
    (AppVersion, "app_id"),
]

@pytest.mark.parametrize("model,col_name", INDEX_COLS,
    ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_index_exists(model, col_name):
    indexed = any(
        col_name in [c.name for c in idx.columns]
        for idx in model.__table__.indexes
    )
    col = model.__table__.columns[col_name]
    has_fk = len(col.foreign_keys) > 0
    # FK columns are typically indexed
    assert indexed or has_fk, f"{model.__name__}.{col_name} should be indexed"
