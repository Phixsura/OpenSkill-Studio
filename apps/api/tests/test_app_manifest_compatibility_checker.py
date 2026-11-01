from app.services.app_manifest_compatibility_checker import check_compatibility

def test_compatible():
    r = check_compatibility({"schema_version": "1.0", "sandbox": {"runtime": "python3.12"}})
    assert r["compatible"] is True

def test_bad_schema():
    r = check_compatibility({"schema_version": "99.0"})
    assert r["compatible"] is False

def test_bad_runtime():
    r = check_compatibility({"schema_version": "1.0", "sandbox": {"runtime": "ruby3.2"}})
    assert r["compatible"] is False

def test_no_sandbox():
    r = check_compatibility({"schema_version": "1.0"})
    assert r["compatible"] is True

def test_platform_version_included():
    r = check_compatibility({"schema_version": "1.0"})
    assert "platform_version" in r
