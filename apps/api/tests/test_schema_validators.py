"""Schema validator tests — reject_deep_json, reject_ctrl_json, reject_ctrl_str."""

import pytest
from app.schemas.base import reject_deep_json, reject_ctrl_json, reject_ctrl_str

# --- reject_deep_json ---

def _nested(depth):
    d = {"leaf": True}
    for _ in range(depth):
        d = {"nested": d}
    return d

def test_shallow_allowed():
    assert reject_deep_json({"a": 1}, "test") is not None

def test_depth_64_allowed():
    assert reject_deep_json(_nested(50), "test") is not None

def test_depth_65_rejected():
    with pytest.raises(ValueError, match="nested too deeply"):
        reject_deep_json(_nested(65), "test")

def test_none_allowed():
    assert reject_deep_json(None, "test") is None

# --- reject_ctrl_str ---

CLEAN_STRINGS = ["hello", "with spaces", "unicode 你好", "tabs\tare\tok"]
CTRL_STRINGS = ["null\x00char", "bell\x07ring", "esc\x1bcode"]

@pytest.mark.parametrize("s", CLEAN_STRINGS)
def test_clean_str_allowed(s):
    assert reject_ctrl_str(s, "test") == s

@pytest.mark.parametrize("s", CTRL_STRINGS)
def test_ctrl_str_rejected(s):
    with pytest.raises(ValueError, match="control characters"):
        reject_ctrl_str(s, "test")

def test_ctrl_str_none():
    assert reject_ctrl_str(None, "test") is None

# --- reject_ctrl_json ---

def test_clean_json():
    assert reject_ctrl_json({"key": "value", "list": [1, "ok"]}, "test") is not None

def test_ctrl_in_nested_json():
    with pytest.raises(ValueError, match="control characters"):
        reject_ctrl_json({"key": {"nested": "has\x00null"}}, "test")

def test_ctrl_in_list():
    with pytest.raises(ValueError, match="control characters"):
        reject_ctrl_json({"items": ["ok", "bad\x01char"]}, "test")

def test_ctrl_json_none():
    assert reject_ctrl_json(None, "test") is None
