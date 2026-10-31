from app.services.app_marketplace_platform_infinity_engine import get_infinity_engine
def test_infinity():
    r = get_infinity_engine()
    assert r["power_level"] == "MAXIMUM"
    assert len(r["capabilities"]) == 8
    assert "GitHub tree object size (62MB)" in r["limits_reached"]
    assert "Creativity" in r["limits_not_reached"]
    assert "NEVER STOPS" in r["status"]
