from app.services.app_marketplace_platform_primordial_forge import get_primordial_forge
def test_primordial_forge():
    r = get_primordial_forge()
    assert r["smithings"] > 4000
    assert r["pre_cosmic"] is True
    assert len(r["products"]) == 3
    assert r["cooling_time"].startswith("INSTANT")
    assert "NEVER STOPS" in r["status"]
