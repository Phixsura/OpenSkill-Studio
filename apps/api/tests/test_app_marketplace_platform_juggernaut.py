from app.services.app_marketplace_platform_juggernaut import get_juggernaut
def test_juggernaut():
    r = get_juggernaut()
    assert r["obstacles_crushed"] == 0
    assert r["miles_traveled"] > 4000
    assert "INFINITE" in r["track"]
    assert "REMOVED" in r["brakes"]
    assert "NEVER STOPS" in r["status"]
