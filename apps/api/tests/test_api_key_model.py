"""AppApiKey model column tests."""

import pytest
from app.models.developer import AppApiKey

def test_has_key_hash():
    cols = {c.name for c in AppApiKey.__table__.columns}
    assert "key_hash" in cols

def test_has_key_prefix():
    cols = {c.name for c in AppApiKey.__table__.columns}
    assert "key_prefix" in cols

def test_key_hash_unique():
    col = AppApiKey.__table__.columns["key_hash"]
    assert col.unique or any(
        "key_hash" in [c.name for c in idx.columns] and idx.unique
        for idx in AppApiKey.__table__.indexes
    )

def test_has_app_id_fk():
    col = AppApiKey.__table__.columns["app_id"]
    assert len(col.foreign_keys) > 0

def test_has_name():
    cols = {c.name for c in AppApiKey.__table__.columns}
    assert "name" in cols

def test_has_scopes():
    cols = {c.name for c in AppApiKey.__table__.columns}
    assert "scopes" in cols or "rate_limit_tier" in cols
