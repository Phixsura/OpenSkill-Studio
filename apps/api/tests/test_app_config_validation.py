"""Tests for app config schema validation in manifests."""

from app.services.manifest_validator import validate_manifest


def test_config_schema_object_type():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "config_schema": {"type": "object", "properties": {"url": {"type": "string"}}}})
    config_warns = [w for w in r.warnings if "config_schema" in w]
    assert config_warns == []

def test_config_schema_array_type_warns():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "config_schema": {"type": "array"}})
    assert any("object" in w for w in r.warnings)

def test_config_schema_with_required():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "config_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}})
    assert r.valid

def test_no_config_schema():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}})
    config_warns = [w for w in r.warnings if "config" in w]
    assert config_warns == []

def test_manifest_runtime_nodejs20():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"runtime": "nodejs20"}})
    runtime_warns = [w for w in r.warnings if "runtime" in w]
    assert runtime_warns == []

def test_manifest_runtime_python312():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"runtime": "python3.12"}})
    runtime_warns = [w for w in r.warnings if "runtime" in w]
    assert runtime_warns == []

def test_manifest_unknown_runtime_warns():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "sandbox": {"runtime": "deno2.0"}})
    assert any("runtime" in w for w in r.warnings)

def test_manifest_egress_allowlist():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "sandbox": {"network": {"egress_policy": "allowlist"}}})
    egress_warns = [w for w in r.warnings if "egress" in w]
    assert egress_warns == []

def test_manifest_egress_deny_all():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "sandbox": {"network": {"egress_policy": "deny_all"}}})
    egress_warns = [w for w in r.warnings if "egress" in w]
    assert egress_warns == []

def test_manifest_egress_unknown_warns():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "sandbox": {"network": {"egress_policy": "allow_all"}}})
    assert any("egress" in w for w in r.warnings)
