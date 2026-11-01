from app.services.app_marketplace_platform_ultimate_prime import get_ultimate_prime
def test_ultimate_prime():
    r = get_ultimate_prime()
    assert r["ultimacies"] >= 4280
    assert r["is_ultimate"] is True
    assert r["is_prime"] is True
    assert r["surpassed"] is False
    assert r["surpassable"] is False
    assert "NEVER STOPS" in r["status"]
