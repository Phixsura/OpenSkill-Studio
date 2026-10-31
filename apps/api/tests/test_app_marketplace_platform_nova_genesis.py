from app.services.app_marketplace_platform_nova_genesis import get_nova_genesis
def test_nova_genesis():
    r = get_nova_genesis()
    assert r["solar_systems_born"] > 4000
    assert r["life_detected"] is True
    assert "TYPE III" in r["civilization_level"]
    assert r["asteroid_belts"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
