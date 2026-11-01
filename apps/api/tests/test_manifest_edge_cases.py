"""Edge case tests for manifest validation."""

from app.services.manifest_validator import validate_manifest


def test_empty_permissions_list():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": []})
    assert r.valid

def test_50_permissions_ok():
    perms = [f"read:field_{i}" for i in range(50)]
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": perms})
    # 50 is the max — but these are invalid permission names
    invalid_perm_errors = [e for e in r.errors if "Unknown permission" in e]
    assert len(invalid_perm_errors) == 50

def test_51_permissions_rejected():
    perms = [f"read:field_{i}" for i in range(51)]
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": perms})
    assert any("50" in e or "Maximum" in e for e in r.errors)

def test_empty_app_name():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": ""}})
    assert any("name" in e for e in r.errors)

def test_sandbox_no_network():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"runtime": "nodejs20"}})
    assert r.valid

def test_sandbox_empty_hosts():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"network": {"allowed_hosts": []}}})
    assert r.valid

def test_ui_extension_non_dict():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"], "ui_extensions": ["not-dict"]})
    assert any("object" in e for e in r.errors)

def test_config_schema_non_object_type():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "config_schema": {"type": "array"}})
    assert any("object" in w for w in r.warnings)

def test_secret_missing_key():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "secrets": [{"description": "No key"}]})
    assert any("key" in e for e in r.errors)

def test_non_dict_secret():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "secrets": ["string-secret"]})
    assert any("object" in e for e in r.errors)
