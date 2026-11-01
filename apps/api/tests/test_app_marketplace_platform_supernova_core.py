from app.services.app_marketplace_platform_supernova_core import get_supernova_core
def test_supernova_core():
    r = get_supernova_core()
    assert r["explosions"] > 4000
    assert len(r["heavy_elements"]) == 3
    assert "Type Ia" in r["type"]
    assert "neutron star" in r["remnant"]
    assert "NEVER STOPS" in r["status"]
