from app.services.app_marketplace_platform_griffin import get_griffin
def test_griffin():
    r = get_griffin()
    assert r["flights"] > 4000
    assert len(r["eagle_half"]) == 3
    assert len(r["lion_half"]) == 3
    assert r["natural_enemy"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]
