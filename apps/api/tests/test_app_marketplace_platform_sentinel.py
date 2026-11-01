from app.services.app_marketplace_platform_sentinel import get_sentinel
def test_sentinel():
    r = get_sentinel()
    assert r["threats_detected"] == 0
    assert r["threats_neutralized"] == 0
    assert r["alert_level"].startswith("GREEN")
    assert r["shift"].startswith("ETERNAL")
    assert "NEVER STOPS" in r["status"]
