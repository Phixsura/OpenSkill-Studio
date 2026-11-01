from app.services.app_marketplace_platform_cosmic_forge_prime import get_cosmic_forge_prime
def test_cosmic_forge_prime():
    r = get_cosmic_forge_prime()
    assert r["realities_forged"] > 4000
    assert r["defective_realities"] == 0
    assert len(r["subordinate_forges"]) == 5
    assert "NEVER STOPS" in r["status"]
