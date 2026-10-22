"""AppEventSubscription model tests."""

import pytest
from app.models.developer import AppEventSubscription

COLS = ["id", "installation_id", "event_type", "enabled", "created_at"]

@pytest.mark.parametrize("col", COLS)
def test_column_exists(col):
    assert col in {c.name for c in AppEventSubscription.__table__.columns}

def test_installation_id_fk():
    assert len(AppEventSubscription.__table__.columns["installation_id"].foreign_keys) > 0

def test_event_type_not_nullable():
    assert not AppEventSubscription.__table__.columns["event_type"].nullable

def test_enabled_has_default():
    col = AppEventSubscription.__table__.columns["enabled"]
    assert col.default is not None or not col.nullable
