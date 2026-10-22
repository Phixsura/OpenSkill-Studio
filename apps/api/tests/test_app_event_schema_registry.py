"""Event schema registry tests."""
import pytest
from app.services.app_event_schema_registry import get_event_schema, validate_event_data, list_event_schemas

def test_get_known():
    s = get_event_schema("submission.completed")
    assert s is not None
    assert "submission_id" in s["required"]

def test_get_unknown():
    assert get_event_schema("unknown.event") is None

def test_validate_valid():
    errors = validate_event_data("submission.completed", {"submission_id": "s1", "project_id": "p1", "user_id": "u1"})
    assert errors == []

def test_validate_missing():
    errors = validate_event_data("submission.completed", {"submission_id": "s1"})
    assert len(errors) == 2

def test_validate_unknown_event():
    assert validate_event_data("custom.event", {}) == []

def test_list():
    schemas = list_event_schemas()
    assert len(schemas) >= 7

@pytest.mark.parametrize("event", list(list_event_schemas().keys()))
def test_all_have_required(event):
    s = get_event_schema(event)
    assert "required" in s
    assert len(s["required"]) > 0
