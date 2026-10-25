from app.services.app_marketplace_platform_cosmic_prime_alpha import get_cosmic_prime_alpha
def test_cosmic_prime_alpha():
    r = get_cosmic_prime_alpha()
    assert r["new_words"] > 4000
    assert r["first_word"].startswith("ALPHA")
    assert r["vocabulary"].startswith("EXPANDING")
    assert "commit" in r["grammar"]
    assert "NEVER STOPS" in r["status"]
