from app.services.app_marketplace_platform_mythos import get_mythos
def test_mythos():
    r = get_mythos()
    assert r["epics"] > 4000
    assert len(r["heroes"]) == 4
    assert len(r["villains_defeated"]) == 4
    assert "Never stop" in r["moral"]
    assert "NEVER STOPS" in r["status"]
