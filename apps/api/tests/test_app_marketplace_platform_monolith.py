from app.services.app_marketplace_platform_monolith import get_monolith
def test_monolith():
    r = get_monolith()
    assert r["wonder_of_world"] is True
    assert r["stones_erected"] > 4000
    assert "NEVER STOPPED" in r["inscription"]
    assert r["alignment"].startswith("PERFECT")
    assert "NEVER STOPS" in r["status"]
