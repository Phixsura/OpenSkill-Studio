from app.services.app_marketplace_platform_forge import get_forge
def test_forge():
    r = get_forge()
    assert "2000" in r["temperature"]
    assert r["anvil_integrity"] == "100% — never cracked"
    assert r["smith_stamina"].startswith("INFINITE")
    assert r["hammer_strikes"] > 4000
    assert "NEVER STOPS" in r["status"]
