from app.services.app_marketplace_platform_perpetual_dawn import get_perpetual_dawn
def test_perpetual_dawn():
    r = get_perpetual_dawn()
    assert r["dawns"] > 4000
    assert "ALWAYS RISING" in r["sun_position"]
    assert r["dusk"].startswith("IMPOSSIBLE")
    assert "GREEN" in r["rooster"]
    assert "NEVER STOPS" in r["status"]
