"""Manifest with all features combined — stress test."""

import pytest
from app.services.manifest_validator import validate_manifest, VALID_PERMISSIONS, VALID_SURFACES

def test_max_permissions():
    """Manifest with ALL 42+ permissions."""
    m = {
        "schema_version": "1.0",
        "app": {"name": "Max Perms", "slug": "max-perms", "version": "1.0.0", "category": "connector"},
        "permissions": list(VALID_PERMISSIONS),
    }
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_all_surfaces():
    """Manifest with ALL UI surfaces."""
    extensions = [{"surface": s, "title": f"Ext {s}", "entry": f"{s}.html"} for s in VALID_SURFACES]
    m = {
        "schema_version": "1.0",
        "app": {"name": "All Surfaces", "slug": "all-surfaces", "version": "1.0.0", "category": "ui_extension"},
        "permissions": ["extend:ui"],
        "ui_extensions": extensions,
    }
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_everything_combined():
    """Maximum manifest with every feature."""
    m = {
        "schema_version": "1.0",
        "app": {"name": "Everything", "slug": "everything-app", "version": "3.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts", "read:projects", "write:projects",
                        "subscribe:events", "extend:ui", "run:background_jobs", "read:analytics"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 512, "timeout_seconds": 120,
                     "network": {"allowed_hosts": ["api.example.com", "hooks.slack.com"], "egress_policy": "allowlist"}},
        "event_subscriptions": ["submission.completed", "submission.graded", "cohort.member_added"],
        "ui_extensions": [
            {"surface": "dashboard_card", "title": "Card", "entry": "card.html", "viewport": {"width": 400, "height": 300}},
            {"surface": "project_sidebar", "title": "Sidebar", "entry": "sidebar.html"},
        ],
        "secrets": [{"key": "API_KEY", "required": True}, {"key": "TOKEN"}, {"key": "SECRET", "required": False}],
        "config_schema": {"type": "object", "properties": {"url": {"type": "string"}, "timeout": {"type": "integer"}}},
    }
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"
    assert r.warnings == [] or isinstance(r.warnings, list)
