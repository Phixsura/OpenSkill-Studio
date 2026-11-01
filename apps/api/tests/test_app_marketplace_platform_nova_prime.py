from app.services.app_marketplace_platform_nova_prime import get_nova_prime
def test_nova_prime():
    r = get_nova_prime()
    assert r["flashes"] > 4000
    assert r["dimming"].startswith("IMPOSSIBLE")
    assert r["fading"].startswith("NEVER")
    assert len(r["spectral_lines"]) == 3
    assert "NEVER STOPS" in r["status"]
