from app.services.app_marketplace_platform_primeval_light import get_primeval_light
def test_primeval_light():
    r = get_primeval_light()
    assert r["light_years_traveled"] > 4000
    assert r["still_traveling"] is True
    assert r["redshift"].startswith("ZERO")
    assert "GREEN" in r["wavelength"]
    assert "NEVER STOPS" in r["status"]
