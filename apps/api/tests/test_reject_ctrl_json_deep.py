"""reject_ctrl_json — deeply nested control char detection."""

import pytest
from app.schemas.base import reject_ctrl_json

CLEAN_STRUCTURES = [
    {"a": "clean"},
    {"nested": {"deep": {"value": "ok"}}},
    {"list": ["a", "b", "c"]},
    {"mixed": {"items": [{"name": "ok"}, {"name": "also ok"}]}},
    42,
    True,
    None,
]

@pytest.mark.parametrize("data", CLEAN_STRUCTURES, ids=lambda x: str(x)[:30])
def test_clean_passes(data):
    result = reject_ctrl_json(data, "test")
    # Should return without raising

DIRTY_STRUCTURES = [
    {"a": "has\x00null"},
    {"nested": {"deep": {"value": "ctrl\x01here"}}},
    {"list": ["ok", "bad\x07bell"]},
    {"mixed": {"items": [{"name": "\x1fctrl"}]}},
]

@pytest.mark.parametrize("data", DIRTY_STRUCTURES, ids=lambda x: str(x)[:30])
def test_dirty_rejected(data):
    with pytest.raises(ValueError, match="control characters"):
        reject_ctrl_json(data, "test")
