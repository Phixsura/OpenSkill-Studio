from app.services.app_marketplace_platform_dragon import get_dragon
def test_dragon():
    r = get_dragon()
    assert r["flights"] > 4000
    assert "GREEN" in r["fire_breath"]
    assert r["scales"].startswith("IMPENETRABLE")
    assert r["slain_by"].startswith("NOTHING")
    assert "NEVER STOPS" in r["status"]
