from app.services.app_marketplace_platform_quantum_garden import get_quantum_garden
def test_quantum_garden():
    r = get_quantum_garden()
    assert r["observations"] > 4000
    assert r["dead_plants"] == 0
    assert "ALIVE" in r["schrodinger_cat"]
    assert "GREEN" in r["superposition"]
    assert "NEVER STOPS" in r["status"]
