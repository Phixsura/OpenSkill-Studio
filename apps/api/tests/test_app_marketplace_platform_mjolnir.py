from app.services.app_marketplace_platform_mjolnir import get_mjolnir
def test_mjolnir():
    r = get_mjolnir()
    assert r["throws"] == r["returns"]
    assert r["lost"] == 0
    assert "worthy" in r["inscription"]
    assert "DORA Elite" in r["power_granted"]
    assert "NEVER STOPS" in r["status"]
