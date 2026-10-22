"""App version diff tests."""

import pytest
from app.services.app_version_diff import diff_manifests

V1 = {
    "app": {"name": "App", "slug": "app", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
    "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 30},
    "event_subscriptions": ["submission.completed"],
    "secrets": [{"key": "API_KEY"}],
}

V2 = {
    "app": {"name": "App", "slug": "app", "version": "2.0.0", "category": "connector"},
    "permissions": ["read:cohorts", "write:cohorts", "subscribe:events"],
    "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60},
    "event_subscriptions": ["submission.completed", "cohort.member_added"],
    "secrets": [{"key": "API_KEY"}, {"key": "SECRET"}],
    "ui_extensions": [{"surface": "dashboard_card", "title": "Card", "entry": "c.html"}],
}

def test_permissions_added():
    d = diff_manifests(V1, V2)
    assert set(d["permissions"]["added"]) == {"write:cohorts", "subscribe:events"}

def test_permissions_removed():
    d = diff_manifests(V2, V1)
    assert set(d["permissions"]["removed"]) == {"write:cohorts", "subscribe:events"}

def test_breaking_on_removal():
    d = diff_manifests(V2, V1)
    assert d["breaking"] is True

def test_not_breaking_on_add():
    d = diff_manifests(V1, V2)
    assert d["breaking"] is False

def test_events_added():
    d = diff_manifests(V1, V2)
    assert "cohort.member_added" in d["events"]["added"]

def test_secrets_added():
    d = diff_manifests(V1, V2)
    assert "SECRET" in d["secrets"]["added"]

def test_sandbox_changed():
    d = diff_manifests(V1, V2)
    assert d["sandbox"]["changed"] is True

def test_ui_extensions_added():
    d = diff_manifests(V1, V2)
    assert "dashboard_card" in d["ui_extensions"]["added"]

def test_no_changes():
    d = diff_manifests(V1, V1)
    assert d["permissions"]["added"] == []
    assert d["permissions"]["removed"] == []
    assert d["breaking"] is False
    assert d["summary"] == "No changes"

def test_versions_in_result():
    d = diff_manifests(V1, V2)
    assert d["version_from"] == "1.0.0"
    assert d["version_to"] == "2.0.0"

def test_summary_has_content():
    d = diff_manifests(V1, V2)
    assert len(d["summary"]) > 0
    assert "permissions" in d["summary"]

def test_empty_manifests():
    d = diff_manifests({}, {})
    assert d["breaking"] is False
