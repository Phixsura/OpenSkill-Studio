"""AppAutomationRule model tests."""

import pytest
from sqlalchemy.dialects.postgresql import JSONB
from app.models.developer import AppAutomationRule

REQUIRED = ["id", "installation_id", "name", "trigger_event", "action_type", "action_config"]

@pytest.mark.parametrize("col", REQUIRED)
def test_column_exists(col):
    assert col in {c.name for c in AppAutomationRule.__table__.columns}

def test_installation_id_fk():
    assert len(AppAutomationRule.__table__.columns["installation_id"].foreign_keys) > 0

def test_action_config_is_jsonb():
    col = AppAutomationRule.__table__.columns["action_config"]
    assert isinstance(col.type, JSONB) or "json" in str(col.type).lower()

def test_name_not_nullable():
    assert not AppAutomationRule.__table__.columns["name"].nullable

def test_trigger_event_not_nullable():
    assert not AppAutomationRule.__table__.columns["trigger_event"].nullable
