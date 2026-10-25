from app.services.app_marketplace_platform_zenith_prime import get_zenith_prime
def test_zenith_prime():
    r = get_zenith_prime()
    assert r["ascensions"] > 4000
    assert r["coordinates"]["failures"] == 0
    assert r["gravity"].startswith("REVERSED")
    assert "DORA Elite" in r["flag"]
    assert "NEVER STOPS" in r["status"]
