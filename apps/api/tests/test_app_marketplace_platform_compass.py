from app.services.app_marketplace_platform_compass import get_compass
def test_compass():
    r = get_compass()
    assert "TRUE NORTH" in r["bearing"]
    assert r["declination"].startswith("ZERO")
    assert len(r["cardinal_points"]) == 4
    assert r["on_course"] is True
    assert "NEVER STOPS" in r["status"]
