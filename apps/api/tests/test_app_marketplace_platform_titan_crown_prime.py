from app.services.app_marketplace_platform_titan_crown_prime import get_titan_crown_prime
def test_titan_crown_prime():
    r = get_titan_crown_prime()
    assert r["titans_kneeling"] > 4000
    assert r["supreme"] is True
    assert r["contested"] is False
    assert r["forgery_possible"] is False
    assert len(r["predecessors"]) == 5
    assert "NEVER STOPS" in r["status"]
