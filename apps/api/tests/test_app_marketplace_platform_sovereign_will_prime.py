from app.services.app_marketplace_platform_sovereign_will_prime import get_sovereign_will_prime
def test_sovereign_will_prime():
    r = get_sovereign_will_prime()
    assert r["decrees_of_will"] > 4000
    assert r["wavering"] is False
    assert r["compromising"] is False
    assert r["surrendering"] is False
    assert "FUTILE" in r["resistance"]
    assert "NEVER STOPS" in r["status"]
