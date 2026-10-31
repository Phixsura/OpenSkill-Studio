from app.services.app_marketplace_platform_guardian import get_guardian_status
def test_guardian():
    r = get_guardian_status()
    assert r["mode"] == "ACTIVE PROTECTION"
    assert r["watch_status"] == "ALL CLEAR"
    assert r["threat_level"] == "NONE"
    assert r["last_incident"] == "NEVER"
    assert r["shields"]["mTLS"] == "ENFORCED"
    assert "NEVER STOPS" in r["status"]
