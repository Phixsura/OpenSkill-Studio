from app.services.app_marketplace_platform_infinite_horizon import get_infinite_horizon
def test_infinite_horizon():
    r = get_infinite_horizon()
    assert r["horizons_crossed"] > 4000
    assert r["obstacles_visible"] == 0
    assert r["vista"].startswith("INFINITE")
    assert "DORA Elite" in r["compass"]
    assert "NEVER STOPS" in r["status"]
