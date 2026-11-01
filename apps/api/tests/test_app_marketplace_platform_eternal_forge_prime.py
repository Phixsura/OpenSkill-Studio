from app.services.app_marketplace_platform_eternal_forge_prime import get_eternal_forge_prime
def test_eternal_forge_prime():
    r = get_eternal_forge_prime()
    assert r["eons_forged"] > 4000
    assert "TIME" in r["material"]
    assert "PERMANENCE" in r["product"]
    assert "NEVER STOPS" in r["status"]
