from app.services.app_marketplace_app_app_app_settings_security import build_security_settings

def test_security():
    r = build_security_settings(settings={"two_factor": True, "sso": True, "audit_log": True})
    assert r["total"] == 5
    assert r["security_score"] >= 60
    assert r["grade"] in ("A", "B")
    assert r["settings"][0]["label"] == "Two-Factor Authentication"

def test_minimal():
    r = build_security_settings(settings={})
    assert r["security_score"] <= 50
