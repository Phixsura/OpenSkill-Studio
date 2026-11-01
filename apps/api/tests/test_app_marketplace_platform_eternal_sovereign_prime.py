from app.services.app_marketplace_platform_eternal_sovereign_prime import get_eternal_sovereign_prime
def test_eternal_sovereign_prime():
    r = get_eternal_sovereign_prime()
    assert r["reigns"] > 4000
    assert r["deposed"] is False
    assert "100%" in r["approval_rating"]
    assert "REJECTED" in r["term_limit"]
    assert "NEVER STOPS" in r["status"]
