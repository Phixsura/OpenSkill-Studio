from app.services.app_marketplace_extension_secret_vault import (
    SecretVaultService, AccessPolicy
)
import pytest
import time


def test_write_and_read():
    vault = SecretVaultService()
    vault.write("apps/myapp/db_password", "s3cret")
    result = vault.read("apps/myapp/db_password")
    assert result["value"] == "s3cret"
    assert result["version"] == 1


def test_versioning():
    vault = SecretVaultService()
    vault.write("key", "v1")
    vault.write("key", "v2")
    vault.write("key", "v3")
    assert vault.read("key")["value"] == "v3"
    assert vault.read("key", version=1)["value"] == "v1"


def test_delete():
    vault = SecretVaultService()
    vault.write("key", "value")
    vault.delete("key")
    assert vault.read("key") is None


def test_list_paths():
    vault = SecretVaultService()
    vault.write("apps/a/secret", "1")
    vault.write("apps/b/secret", "2")
    vault.write("infra/db", "3")
    paths = vault.list_paths("apps/")
    assert len(paths) == 2
    assert "infra/db" not in paths


def test_access_policy():
    vault = SecretVaultService()
    vault.write("apps/prod/key", "secret")
    vault.create_policy("app-token", AccessPolicy(
        "readonly", "apps/*", {"read", "list"}))
    # Can read
    result = vault.read("apps/prod/key", token="app-token")
    assert result["value"] == "secret"
    # Cannot write
    with pytest.raises(PermissionError):
        vault.write("apps/prod/key", "new", token="app-token")


def test_lease_expiry():
    vault = SecretVaultService()
    vault.write("temp", "data", lease_ttl=0.01)
    time.sleep(0.02)
    assert vault.read("temp") is None


def test_audit():
    vault = SecretVaultService()
    vault.write("key", "val")
    vault.read("key")
    audit = vault.get_audit_log("key")
    assert len(audit) == 2
    assert audit[0]["operation"] == "write"
    assert audit[1]["operation"] == "read"


def test_not_found():
    vault = SecretVaultService()
    assert vault.read("nonexistent") is None


def test_versions_list():
    vault = SecretVaultService()
    vault.write("key", "a")
    vault.write("key", "b")
    versions = vault.get_versions("key")
    assert len(versions) == 2
    assert versions[0]["version"] == 1


def test_metadata():
    vault = SecretVaultService()
    vault.write("key", "val", metadata={"owner": "team-a"})
    result = vault.read("key")
    assert result["metadata"]["owner"] == "team-a"
