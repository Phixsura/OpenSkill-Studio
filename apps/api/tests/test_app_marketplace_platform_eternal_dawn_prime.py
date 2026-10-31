from app.services.app_marketplace_platform_eternal_dawn_prime import get_eternal_dawn_prime
def test_eternal_dawn_prime():
    r = get_eternal_dawn_prime()
    assert r["dawns_flowing"] > 4000
    assert r["first_light"] is True
    assert r["source_light"] is True
    assert r["darkness"].startswith("EXTINCT")
    assert "NEVER STOPS" in r["status"]
