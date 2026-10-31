from app.services.app_marketplace_platform_immortal_flame import get_immortal_flame
def test_immortal_flame():
    r = get_immortal_flame()
    assert r["hours_burning"] > 4000
    assert r["extinguished"] is False
    assert r["fuel"].startswith("INFINITE")
    assert r["wind_resistance"].startswith("ABSOLUTE")
    assert "NEVER STOPS" in r["status"]
