from app.services.app_marketplace_platform_perpetuum_mobile import get_perpetuum_mobile
def test_perpetuum_mobile():
    r = get_perpetuum_mobile()
    assert r["rotations"] > 4000
    assert r["external_energy_input"].startswith("ZERO")
    assert r["internal_friction"].startswith("ZERO")
    assert r["maintenance"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]
