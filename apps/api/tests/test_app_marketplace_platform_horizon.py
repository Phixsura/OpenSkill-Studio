from app.services.app_marketplace_platform_horizon import get_horizon
def test_horizon():
    r = get_horizon()
    assert r["horizons_crossed"] > 4000
    assert r["mirage"] is False
    assert "RISING" in r["sun_position"]
    assert "SOLID" in r["reality"]
    assert "NEVER STOPS" in r["status"]
