"""Tests for every permission scope in the manifest validator."""

from app.services.manifest_validator import VALID_PERMISSIONS, validate_manifest


def test_every_valid_permission_accepted():
    """Each of the 42 valid permissions is accepted individually."""
    for perm in sorted(VALID_PERMISSIONS):
        r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": [perm]})
        perm_errors = [e for e in r.errors if "Unknown permission" in e]
        assert perm_errors == [], f"Valid permission '{perm}' rejected"


def test_invalid_permissions_rejected():
    invalid = ["hack:system", "admin:delete", "root:all", "sudo:exec", "write:database"]
    for perm in invalid:
        r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": [perm]})
        assert any("Unknown permission" in e for e in r.errors), f"'{perm}' should be rejected"


def test_all_read_permissions():
    read_perms = [p for p in VALID_PERMISSIONS if p.startswith("read:")]
    assert len(read_perms) >= 10


def test_all_write_permissions():
    write_perms = [p for p in VALID_PERMISSIONS if p.startswith("write:")]
    assert len(write_perms) >= 5


def test_special_permissions():
    special = {"subscribe:events", "extend:ui", "export:analytics", "run:background_jobs"}
    for perm in special:
        assert perm in VALID_PERMISSIONS, f"Missing special permission: {perm}"


def test_permission_count():
    assert len(VALID_PERMISSIONS) >= 30


def test_all_permissions_colon_separated():
    for perm in VALID_PERMISSIONS:
        assert ":" in perm, f"Permission '{perm}' missing colon"
        parts = perm.split(":")
        assert len(parts) == 2, f"Permission '{perm}' should have exactly one colon"


def test_all_permissions_lowercase():
    for perm in VALID_PERMISSIONS:
        assert perm == perm.lower(), f"Permission '{perm}' not lowercase"
