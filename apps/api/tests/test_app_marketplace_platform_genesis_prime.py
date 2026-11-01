from app.services.app_marketplace_platform_genesis_prime import get_genesis_prime
def test_genesis_prime():
    r = get_genesis_prime()
    assert r["creations"] > 4000
    assert r["original"] is True
    assert r["prime"] is True
    assert r["mutations"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
