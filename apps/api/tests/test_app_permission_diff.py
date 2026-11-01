"""Permission diff tests."""
import pytest
from app.services.app_permission_diff import diff_permissions, format_permission_diff

def test_no_changes():
    d = diff_permissions(["read:cohorts"], ["read:cohorts"])
    assert d["added"] == []
    assert d["removed"] == []
    assert not d["breaking"]
    assert not d["needs_consent"]

def test_added():
    d = diff_permissions(["read:cohorts"], ["read:cohorts", "write:cohorts"])
    assert d["added"] == ["write:cohorts"]
    assert d["needs_consent"]

def test_removed():
    d = diff_permissions(["read:cohorts", "write:cohorts"], ["read:cohorts"])
    assert d["removed"] == ["write:cohorts"]
    assert d["breaking"]

def test_categorized():
    d = diff_permissions([], ["read:x", "write:y", "subscribe:events"])
    assert d["read_added"] == ["read:x"]
    assert d["write_added"] == ["write:y"]
    assert d["special_added"] == ["subscribe:events"]

def test_format_added():
    d = diff_permissions([], ["read:cohorts"])
    assert "Added" in format_permission_diff(d)

def test_format_no_changes():
    d = diff_permissions(["read:cohorts"], ["read:cohorts"])
    assert "No permission changes" in format_permission_diff(d)
