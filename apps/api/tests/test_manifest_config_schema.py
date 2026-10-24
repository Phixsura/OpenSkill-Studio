"""Manifest config_schema validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "X", "slug": "cfg-test", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}

def test_valid_config_schema():
    m = {**BASE, "config_schema": {
        "type": "object",
        "properties": {"api_url": {"type": "string"}, "timeout": {"type": "integer"}},
        "required": ["api_url"],
    }}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_manifest_with_secrets():
    m = {**BASE, "secrets": [
        {"key": "API_KEY", "required": True},
        {"key": "API_SECRET", "required": False},
    ]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_manifest_with_event_subscriptions():
    m = {**BASE, "permissions": ["read:cohorts", "subscribe:events"],
         "event_subscriptions": ["submission.completed", "cohort.member_added"]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_manifest_minimal():
    m = {
        "schema_version": "1.0",
        "app": {"name": "Minimal", "slug": "minimal", "version": "0.1.0", "category": "analytics"},
        "permissions": ["read:analytics"],
    }
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_manifest_all_features():
    m = {
        "schema_version": "1.0",
        "app": {"name": "Full", "slug": "full-app", "version": "3.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "write:cohorts", "subscribe:events", "extend:ui"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60,
                     "network": {"allowed_hosts": ["api.example.com"], "egress_policy": "allowlist"}},
        "event_subscriptions": ["submission.completed"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "Card", "entry": "card.html"}],
        "secrets": [{"key": "TOKEN", "required": True}],
        "config_schema": {"type": "object", "properties": {"url": {"type": "string"}}},
    }
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"
