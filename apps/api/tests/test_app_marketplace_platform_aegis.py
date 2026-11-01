from app.services.app_marketplace_platform_aegis import get_aegis
def test_aegis():
    r = get_aegis()
    assert r["vulnerabilities"] == 0
    assert r["shield_strength"].startswith("DIVINE")
    assert len(r["divine_power"]) == 3
    assert r["threats_deflected"] > 4000
    assert "NEVER STOPS" in r["status"]
