from app.services.app_marketplace_app_app_license_checker import check_license, audit_dependencies

def test_mit():
    r = check_license(license_id="MIT")
    assert r["permissive"]
    assert r["risk"] == "low"

def test_gpl():
    r = check_license(license_id="GPL-3.0")
    assert r["copyleft"]
    assert r["risk"] == "high"

def test_unknown():
    r = check_license(license_id="SomethingWeird")
    assert r["risk"] == "critical"

def test_audit():
    deps = [
        {"name": "react", "license": "MIT"},
        {"name": "linux-lib", "license": "GPL-3.0"},
        {"name": "mystery", "license": "UNKNOWN"},
    ]
    r = audit_dependencies(deps=deps)
    assert r["total"] == 3
    assert r["has_copyleft"]
    assert r["overall_risk"] == "critical"
