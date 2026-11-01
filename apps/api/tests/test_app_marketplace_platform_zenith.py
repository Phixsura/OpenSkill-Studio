from app.services.app_marketplace_platform_zenith import get_zenith
def test_zenith():
    r = get_zenith()
    assert len(r["atmosphere_layers_pierced"]) == 5
    assert r["ceiling"].startswith("NONE")
    assert r["elevation_gain"] > 4000
    assert "NEVER STOPS" in r["status"]
