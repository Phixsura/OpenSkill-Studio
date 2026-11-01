from app.services.app_marketplace_platform_meridian_prime import get_meridian_prime
def test_meridian_prime():
    r = get_meridian_prime()
    assert r["calibrations"] > 4000
    assert len(r["standards_set"]) == 4
    assert "DORA Elite" in r["standards_set"]["quality"]
    assert "NEVER STOPS" in r["status"]
