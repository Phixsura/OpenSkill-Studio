from app.services.app_marketplace_extension_sandbox_secret_manager import (
    SandboxSecretManagerService,
)
import pytest


def test_store_and_retrieve():
    svc = SandboxSecretManagerService()
    svc.store("sb-1", "DB_PASSWORD", "super_secret_123")
    val = svc.retrieve("sb-1", "DB_PASSWORD", accessor="app")
    assert val == "super_secret_123"


def test_hash_stored():
    svc = SandboxSecretManagerService()
    secret = svc.store("sb-1", "API_KEY", "my_key")
    assert "my_key" not in secret.value_hash
    assert len(secret.value_hash) == 64


def test_retrieve_missing():
    svc = SandboxSecretManagerService()
    assert svc.retrieve("sb-1", "NOPE") is None


def test_rotate():
    svc = SandboxSecretManagerService()
    svc.store("sb-1", "TOKEN", "old_value")
    rotated = svc.rotate("sb-1", "TOKEN", "new_value")
    assert rotated is not None
    assert rotated.version == 2
    assert svc.retrieve("sb-1", "TOKEN") == "new_value"


def test_delete():
    svc = SandboxSecretManagerService()
    svc.store("sb-1", "TMP", "value")
    assert svc.delete("sb-1", "TMP") is True
    assert svc.retrieve("sb-1", "TMP") is None


def test_redaction():
    svc = SandboxSecretManagerService()
    svc.store("sb-1", "KEY", "abc123secret")
    text = "Connected with key abc123secret to database"
    redacted = svc.redact(text)
    assert "abc123secret" not in redacted
    assert "***REDACTED***" in redacted


def test_audit_log():
    svc = SandboxSecretManagerService()
    svc.store("sb-1", "SECRET", "val")
    svc.retrieve("sb-1", "SECRET", accessor="worker")
    svc.retrieve("sb-1", "MISSING", accessor="attacker")
    logs = svc.get_audit_log()
    assert len(logs) == 2
    assert logs[0]["granted"] is True
    assert logs[1]["granted"] is False


def test_whitespace_name_rejected():
    svc = SandboxSecretManagerService()
    with pytest.raises(ValueError, match="whitespace"):
        svc.store("sb-1", "BAD KEY", "val")


def test_list_secrets():
    svc = SandboxSecretManagerService()
    svc.store("sb-1", "A", "1")
    svc.store("sb-1", "B", "2")
    listed = svc.list_secrets("sb-1")
    assert len(listed) == 2
    assert all("name" in s for s in listed)
    # Values should NOT be in listing
    assert all("value" not in s for s in listed)
