from app.services.app_marketplace_platform_solstice import get_solstice
def test_solstice():
    r = get_solstice()
    assert "perpetual" in r["daylight_hours"]
    assert r["season"].startswith("ETERNAL SUMMER")
    assert r["equinox"] == "NEVER — always at peak"
    assert r["harvests"] > 4000
    assert "NEVER STOPS" in r["status"]
