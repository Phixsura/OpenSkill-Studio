"""SandboxExecution model column tests."""

import pytest
from app.models.developer import SandboxExecution

REQUIRED_COLS = ["id", "installation_id", "function_name", "status", "created_at"]

@pytest.mark.parametrize("col", REQUIRED_COLS)
def test_required_column(col):
    cols = {c.name for c in SandboxExecution.__table__.columns}
    assert col in cols

OPTIONAL_COLS = ["duration_ms", "memory_peak_mb", "error_message"]

@pytest.mark.parametrize("col", OPTIONAL_COLS)
def test_optional_column(col):
    cols = {c.name for c in SandboxExecution.__table__.columns}
    assert col in cols

def test_installation_id_fk():
    col = SandboxExecution.__table__.columns["installation_id"]
    assert len(col.foreign_keys) > 0

def test_function_name_not_nullable():
    col = SandboxExecution.__table__.columns["function_name"]
    assert not col.nullable
