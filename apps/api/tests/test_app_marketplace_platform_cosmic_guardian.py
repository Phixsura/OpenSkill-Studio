from app.services.app_marketplace_platform_cosmic_guardian import get_cosmic_guardian
def test_cosmic_guardian():
    r = get_cosmic_guardian()
    assert r["vigils"] > 4000
    assert r["on_duty"] == "FOREVER"
    assert r["off_duty"] == "NEVER"
    assert r["threats_remaining"] == 0
    assert "NEVER STOPS" in r["status"]
