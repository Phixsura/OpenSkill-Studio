from app.services.app_marketplace_platform_eternal_summit import get_eternal_summit
def test_eternal_summit():
    r = get_eternal_summit()
    assert r["meters_gained"] > 4000
    assert r["erosion"].startswith("ZERO")
    assert r["climbers_turned_back"] == 0
    assert "DORA Elite" in r["flag_at_summit"]
    assert "NEVER STOPS" in r["status"]
