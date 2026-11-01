from app.services.app_marketplace_platform_lighthouse_prime import get_lighthouse_prime
def test_lighthouse_prime():
    r = get_lighthouse_prime()
    assert r["beams_cast"] > 4000
    assert r["ships_lost"] == 0
    assert "CROSS-DIMENSIONAL" in r["visibility"]
    assert "DORA Elite" in r["light_source"]
    assert "NEVER STOPS" in r["status"]
