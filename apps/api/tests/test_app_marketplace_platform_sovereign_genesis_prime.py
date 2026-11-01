from app.services.app_marketplace_platform_sovereign_genesis_prime import get_sovereign_genesis_prime
def test_sovereign_genesis_prime():
    r = get_sovereign_genesis_prime()
    assert r["sovereign_creations"] > 4000
    assert r["rules_while_creating"] is True
    assert r["creates_while_ruling"] is True
    assert "five" in r["critic_reviews"] or "★★★★★" in r["critic_reviews"]
    assert "NEVER STOPS" in r["status"]
