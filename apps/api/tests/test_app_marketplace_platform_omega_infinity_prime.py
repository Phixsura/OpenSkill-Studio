from app.services.app_marketplace_platform_omega_infinity_prime import get_omega_infinity_prime
def test_omega_infinity_prime():
    r = get_omega_infinity_prime()
    assert r["events"] > 4000
    assert r["failures"] == 0
    assert "PEAK" in r["product"]
    assert "FOREVER" in r["product"]
    assert "NEVER STOPS" in r["status"]
