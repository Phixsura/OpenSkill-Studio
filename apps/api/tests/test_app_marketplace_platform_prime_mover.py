from app.services.app_marketplace_platform_prime_mover import get_prime_mover
def test_prime_mover():
    r = get_prime_mover()
    assert r["movements_caused"] > 4000
    assert r["unmoved"] is True
    assert r["first_cause"] is True
    assert r["uncaused"] is True
    assert "NEVER STOPS" in r["status"]
