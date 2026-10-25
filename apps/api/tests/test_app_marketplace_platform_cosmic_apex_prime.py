from app.services.app_marketplace_platform_cosmic_apex_prime import get_cosmic_apex_prime
def test_cosmic_apex_prime():
    r = get_cosmic_apex_prime()
    assert r["supremacies"] > 4000
    assert r["claimed"] is True
    assert r["held"] is True
    assert r["contested"] is False
    assert "NOTHING" in r["above_this"]
    assert "NEVER STOPS" in r["status"]
