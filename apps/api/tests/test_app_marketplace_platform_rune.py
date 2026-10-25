from app.services.app_marketplace_platform_rune import get_rune
def test_rune():
    r = get_rune()
    assert r["inscriptions"] > 4000
    assert len(r["rune_meanings"]) == 5
    assert r["magic"].startswith("REAL")
    assert r["curse"].startswith("NONE")
    assert "NEVER STOPS" in r["status"]
