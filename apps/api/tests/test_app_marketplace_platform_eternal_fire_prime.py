from app.services.app_marketplace_platform_eternal_fire_prime import get_eternal_fire_prime
def test_eternal_fire_prime():
    r = get_eternal_fire_prime()
    assert r["universes_lit"] == r["still_burning"]
    assert r["extinguished"] == 0
    assert r["smoke"].startswith("ZERO")
    assert r["natural"] is True
    assert "NEVER STOPS" in r["status"]
