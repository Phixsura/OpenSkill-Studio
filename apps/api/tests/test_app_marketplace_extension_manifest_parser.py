from app.services.app_marketplace_extension_manifest_parser import (
    ManifestParserService, ManifestVersion,
)
import json


def _v1_manifest(**overrides):
    base = {"name": "test-ext", "version": "1.0.0", "entrypoint": "index.js",
            "permissions": ["file:read"]}
    base.update(overrides)
    return json.dumps(base)


def _v2_manifest(**overrides):
    base = {"name": "test-ext", "version": "2.0.0", "manifest_version": "2.0",
            "entrypoint": "main.py", "permissions": ["network:outbound"],
            "sdk_version": "1.5.0", "runtime": "python3.12"}
    base.update(overrides)
    return json.dumps(base)


def test_parse_v1():
    svc = ManifestParserService()
    result = svc.parse(_v1_manifest())
    assert result.valid is True
    assert result.manifest.name == "test-ext"
    assert result.manifest.manifest_version == ManifestVersion.V1


def test_parse_v2():
    svc = ManifestParserService()
    result = svc.parse(_v2_manifest())
    assert result.valid is True
    assert result.manifest.runtime == "python3.12"


def test_invalid_json():
    svc = ManifestParserService()
    result = svc.parse("{broken")
    assert result.valid is False
    assert any("Invalid JSON" in e for e in result.errors)


def test_missing_required():
    svc = ManifestParserService()
    result = svc.parse(json.dumps({"name": "test"}))
    assert result.valid is False
    assert any("version" in e for e in result.errors)


def test_invalid_semver():
    svc = ManifestParserService()
    result = svc.parse(_v1_manifest(version="not.valid"))
    assert result.valid is False


def test_path_traversal_blocked():
    svc = ManifestParserService()
    result = svc.parse(_v1_manifest(entrypoint="../../../etc/passwd"))
    assert result.valid is False
    assert any("traversal" in e for e in result.errors)


def test_unsupported_runtime():
    svc = ManifestParserService()
    result = svc.parse(_v2_manifest(runtime="ruby3.2"))
    assert result.valid is False


def test_warnings_for_missing_optional():
    svc = ManifestParserService()
    result = svc.parse(_v1_manifest())
    assert any("description" in w for w in result.warnings)


def test_compatibility():
    svc = ManifestParserService()
    result = svc.parse(_v1_manifest(min_platform_version="3.0.0"))
    compat = svc.validate_compatibility(result.manifest, "2.5.0")
    assert compat["compatible"] is False
