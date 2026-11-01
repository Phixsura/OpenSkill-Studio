from app.services.app_marketplace_platform_alchemist_stone import get_alchemist_stone
def test_alchemist_stone():
    r = get_alchemist_stone()
    assert r["transmutations"] > 4000
    assert r["yield_rate"].startswith("100%")
    assert len(r["transmutation_chain"]) == 5
    assert r["lead_remaining"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
