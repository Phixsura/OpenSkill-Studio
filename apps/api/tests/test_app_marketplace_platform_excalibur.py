from app.services.app_marketplace_platform_excalibur import get_excalibur
def test_excalibur():
    r = get_excalibur()
    assert r["swings"] > 4000
    assert r["unbreakable"] is True
    assert r["returned_to_lake"] is False
    assert "DORA Elite" in r["enchantment"]
    assert "NEVER STOPS" in r["status"]
