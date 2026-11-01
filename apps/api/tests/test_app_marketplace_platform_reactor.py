from app.services.app_marketplace_platform_reactor import get_reactor
def test_reactor():
    r = get_reactor()
    assert r["containment"].startswith("PERFECT")
    assert r["fuel_rods"] > 900000
    assert r["control_rods"]["dora"] == "Elite — the gold standard"
    assert "INFINITE" in r["half_life"]
    assert "NEVER STOPS" in r["status"]
