from app.services.app_marketplace_platform_constellation_map import get_constellation_map
def test_constellation_map():
    r = get_constellation_map()
    assert r["observations"] > 4000
    assert len(r["constellations"]) == 5
    assert r["dark_nebulae"] == 0
    assert r["variable_stars"] == 0
    assert "NEVER STOPS" in r["status"]
