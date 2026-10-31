"""Manifest secrets validation."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {
    "schema_version": "1.0",
    "app": {"name": "Sec", "slug": "sec-app", "version": "1.0.0", "category": "connector"},
    "permissions": ["read:cohorts"],
}

def test_secrets_required_flag():
    m = {**BASE, "secrets": [{"key": "API_KEY", "required": True}]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_secrets_optional():
    m = {**BASE, "secrets": [{"key": "OPT_KEY", "required": False}]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_multiple_secrets():
    m = {**BASE, "secrets": [
        {"key": "API_KEY", "required": True},
        {"key": "API_SECRET", "required": True},
        {"key": "WEBHOOK_TOKEN"},
    ]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_empty_secrets():
    m = {**BASE, "secrets": []}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

SECRET_KEY_NAMES = ["API_KEY", "SECRET_TOKEN", "DB_PASSWORD", "OAUTH_CLIENT_SECRET"]

@pytest.mark.parametrize("key", SECRET_KEY_NAMES)
def test_various_secret_keys(key):
    m = {**BASE, "secrets": [{"key": key, "required": True}]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"
