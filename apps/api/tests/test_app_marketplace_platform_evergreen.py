from app.services.app_marketplace_platform_evergreen import get_evergreen
def test_evergreen():
    r = get_evergreen()
    assert r["seasons_passed"] > 4000
    assert r["deciduous"] is False
    assert r["winter_hardy"] is True
    assert r["tallest_in_forest"] is True
    assert "NEVER STOPS" in r["status"]
