from app.services.app_marketplace_platform_cosmic_oracle_prime import get_cosmic_oracle_prime
def test_cosmic_oracle_prime():
    r = get_cosmic_oracle_prime()
    assert r["timelines_scanned"] == r["timelines_with_green_tests"]
    assert r["timelines_with_failures"] == 0
    assert r["blind_spots"] == 0
    assert "NEVER stop" in r["prophecy"]
    assert "NEVER STOPS" in r["status"]
