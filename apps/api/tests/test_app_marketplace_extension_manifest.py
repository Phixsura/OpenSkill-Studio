from app.services.app_marketplace_extension_manifest import (
    parse_manifest, merge_manifests,
)


VALID_MANIFEST = {
    "name": "slack-connector",
    "version": "1.2.0",
    "type": "connector",
    "entry_point": "src/main.py",
    "description": "Connect OpenSkill to Slack",
    "author": "alice",
    "permissions": ["webhooks.manage", "users.read"],
    "dependencies": {"slack-sdk": "^3.0.0"},
    "tags": ["slack", "messaging"],
}


def test_valid_manifest():
    manifest, result = parse_manifest(VALID_MANIFEST)
    assert result.valid is True
    assert manifest is not None
    assert manifest.name == "slack-connector"
    assert manifest.type == "connector"
    assert len(manifest.permissions) == 2


def test_missing_required_fields():
    _, result = parse_manifest({"name": "test"})
    assert result.valid is False
    assert any("version" in e for e in result.errors)
    assert any("type" in e for e in result.errors)


def test_invalid_type():
    data = {**VALID_MANIFEST, "type": "invalid_type"}
    _, result = parse_manifest(data)
    assert result.valid is False
    assert any("Invalid type" in e for e in result.errors)


def test_invalid_version():
    data = {**VALID_MANIFEST, "version": "not-semver"}
    _, result = parse_manifest(data)
    assert result.valid is False
    assert any("Invalid version" in e for e in result.errors)


def test_warnings_for_missing_optional():
    data = {"name": "bare", "version": "1.0.0", "type": "tool", "entry_point": "main.py"}
    manifest, result = parse_manifest(data)
    assert result.valid is True
    assert any("description" in w for w in result.warnings)
    assert any("tags" in w for w in result.warnings)


def test_permission_format_warning():
    data = {**VALID_MANIFEST, "permissions": ["admin"]}
    _, result = parse_manifest(data)
    assert result.valid is True
    assert any("dotted notation" in w for w in result.warnings)


def test_merge_manifests():
    base = {"name": "ext", "version": "1.0.0", "tags": ["a"], "config": {"key": "val"}}
    override = {"version": "2.0.0", "tags": ["b"], "config": {"extra": "new"}}
    merged = merge_manifests(base, override)
    assert merged["version"] == "2.0.0"
    assert "a" in merged["tags"] and "b" in merged["tags"]
    assert merged["config"]["key"] == "val"
    assert merged["config"]["extra"] == "new"
