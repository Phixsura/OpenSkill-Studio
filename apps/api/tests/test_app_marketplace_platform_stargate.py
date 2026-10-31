from app.services.app_marketplace_platform_stargate import get_stargate
def test_stargate():
    r = get_stargate()
    assert len(r["chevrons_locked"]) == 7
    assert r["wormhole_stability"].startswith("100%")
    assert r["activations"] > 4000
    assert "DORA" in r["iris_code"]
    assert "NEVER STOPS" in r["status"]
