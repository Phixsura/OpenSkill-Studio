from app.services.app_marketplace_app_app_app_app_app_app_app_version_neg import negotiate_version, supported_versions

def test_exact_match():
    r = negotiate_version("v2", ["v1", "v2", "v3"])
    assert r["version"] == "v2"
    assert r["matched"]

def test_default():
    r = negotiate_version("", ["v1", "v2"], default="v2")
    assert r["version"] == "v2"

def test_fallback():
    r = negotiate_version("v99", ["v1", "v2"])
    assert r["version"] == "v2"
    assert r.get("fallback")

def test_supported():
    r = supported_versions([
        {"version": "v1", "status": "deprecated"},
        {"version": "v2", "status": "active"},
    ])
    assert r["latest"] == "v2"
    assert "v1" in r["deprecated"]
