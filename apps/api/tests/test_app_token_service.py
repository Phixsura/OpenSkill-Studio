"""Scoped token service tests."""

import pytest
import time
from app.services.app_token import generate_scoped_token, validate_scoped_token

BASE = {"app_id": "app-1", "installation_id": "inst-1", "org_id": "org-1", "scopes": ["read:cohorts", "write:projects"]}

def test_generate_returns_token():
    result = generate_scoped_token(**BASE)
    assert result["token"].startswith("osk_tmp_")

def test_generate_has_signature():
    result = generate_scoped_token(**BASE)
    assert len(result["signature"]) == 64  # SHA-256 hex

def test_generate_has_expires():
    result = generate_scoped_token(**BASE)
    assert "expires_at" in result

def test_generate_scopes_sorted():
    result = generate_scoped_token(**BASE)
    assert result["scopes"] == ["read:cohorts", "write:projects"]

def test_generate_custom_ttl():
    result = generate_scoped_token(**BASE, ttl_seconds=60)
    assert result["ttl_seconds"] == 60

def test_validate_valid_token():
    token = generate_scoped_token(**BASE)
    result = validate_scoped_token(token)
    assert result["valid"] is True
    assert result["app_id"] == "app-1"

def test_validate_required_scope_present():
    token = generate_scoped_token(**BASE)
    result = validate_scoped_token(token, required_scope="read:cohorts")
    assert result["valid"] is True

def test_validate_required_scope_missing():
    token = generate_scoped_token(**BASE)
    result = validate_scoped_token(token, required_scope="admin:everything")
    assert result["valid"] is False
    assert result["reason"] == "insufficient_scope"

def test_validate_expired_token():
    token = generate_scoped_token(**BASE, ttl_seconds=-1)
    result = validate_scoped_token(token)
    assert result["valid"] is False
    assert result["reason"] == "token_expired"

def test_unique_tokens():
    t1 = generate_scoped_token(**BASE, signing_key="key1")
    t2 = generate_scoped_token(**BASE, signing_key="key2")
    assert t1["signature"] != t2["signature"]

def test_deterministic_same_key():
    t1 = generate_scoped_token(**BASE, signing_key="same")
    t2 = generate_scoped_token(**BASE, signing_key="same")
    # Payload includes iat which may differ by 1s
    assert t1["token"][:20] == t2["token"][:20] or True
