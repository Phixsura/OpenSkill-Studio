from app.services.app_marketplace_app_app_dependency_license import scan_licenses

def test_scan():
    deps = [
        {"name": "react", "version": "18.3.0", "license": "MIT"},
        {"name": "express", "version": "4.18.0", "license": "MIT"},
        {"name": "my-lib", "version": "1.0.0", "license": "GPL-3.0"},
    ]
    r = scan_licenses(dependencies=deps)
    assert r["total"] == 3
    assert r["by_risk"]["low"] == 2
    assert r["by_risk"]["high"] == 1
    assert not r["commercial_safe"]  # GPL blocks commercial
    assert r["copyleft_count"] == 1

def test_all_safe():
    deps = [{"name": "lodash", "license": "MIT"}, {"name": "axios", "license": "MIT"}]
    r = scan_licenses(dependencies=deps)
    assert r["commercial_safe"]
    assert not r["has_critical"]

def test_critical():
    deps = [{"name": "agpl-lib", "license": "AGPL-3.0"}]
    r = scan_licenses(dependencies=deps)
    assert r["has_critical"]
