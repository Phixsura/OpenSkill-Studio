"""Manifest field differ tests."""
import pytest
from app.services.app_manifest_differ import diff_fields, summarize_changes

def test_no_changes():
    assert diff_fields({"a": 1}, {"a": 1}) == []

def test_added():
    changes = diff_fields({}, {"a": 1})
    assert len(changes) == 1
    assert changes[0]["type"] == "added"

def test_removed():
    changes = diff_fields({"a": 1}, {})
    assert len(changes) == 1
    assert changes[0]["type"] == "removed"

def test_changed():
    changes = diff_fields({"a": 1}, {"a": 2})
    assert changes[0]["type"] == "changed"
    assert changes[0]["old_value"] == 1
    assert changes[0]["new_value"] == 2

def test_nested():
    changes = diff_fields({"x": {"y": 1}}, {"x": {"y": 2}})
    assert changes[0]["path"] == "x.y"

def test_summarize():
    changes = [{"type": "added"}, {"type": "removed"}, {"type": "changed"}, {"type": "changed"}]
    s = summarize_changes(changes)
    assert s["total"] == 4
    assert s["added"] == 1
    assert s["changed"] == 2
