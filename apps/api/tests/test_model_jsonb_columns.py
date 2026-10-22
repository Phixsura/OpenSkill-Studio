"""Models with JSONB columns should use PostgreSQL JSONB type."""

import pytest
from sqlalchemy.dialects.postgresql import JSONB
from app.models.developer import (
    AppVersion, AppAutomationRule, AppReviewSubmission,
)

JSONB_COLS = [
    (AppVersion, "manifest"),
    (AppAutomationRule, "action_config"),
    (AppReviewSubmission, "automated_checks"),
]

@pytest.mark.parametrize("model,col_name", JSONB_COLS,
    ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_jsonb_type(model, col_name):
    col = model.__table__.columns[col_name]
    assert isinstance(col.type, JSONB) or "json" in str(col.type).lower()

@pytest.mark.parametrize("model,col_name", JSONB_COLS,
    ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_jsonb_column_exists(model, col_name):
    cols = {c.name for c in model.__table__.columns}
    assert col_name in cols
