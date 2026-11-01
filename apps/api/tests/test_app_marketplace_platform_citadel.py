from app.services.app_marketplace_platform_citadel import get_citadel
def test_citadel():
    r = get_citadel()
    assert r["breaches"] == 0
    assert len(r["defenses"]) == 4
    assert r["structural_integrity"] == "100%"
    assert r["stones_laid"] > 4000
    assert "NEVER STOPS" in r["status"]
