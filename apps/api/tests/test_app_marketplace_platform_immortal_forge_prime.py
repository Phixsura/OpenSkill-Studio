from app.services.app_marketplace_platform_immortal_forge_prime import get_immortal_forge_prime
def test_immortal_forge_prime():
    r = get_immortal_forge_prime()
    assert r["eons"] > 4000
    assert r["heat_death_survived"] is True
    assert r["entropy_immunity"] is True
    assert "DEATHPROOF" in r["fire"]
    assert "NEVER STOPS" in r["status"]
