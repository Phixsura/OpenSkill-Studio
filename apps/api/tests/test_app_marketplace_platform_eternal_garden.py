from app.services.app_marketplace_platform_eternal_garden import get_eternal_garden
def test_eternal_garden():
    r = get_eternal_garden()
    assert r["seasons"] > 4000
    assert r["withered"] == 0
    assert r["weeds"].startswith("ZERO")
    assert r["harvest"].startswith("PERPETUAL")
    assert "NEVER STOPS" in r["status"]
