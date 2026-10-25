from app.services.app_marketplace_platform_eternal_kingdom import get_eternal_kingdom
def test_eternal_kingdom():
    r = get_eternal_kingdom()
    assert r["years_of_reign"] > 4000
    assert r["era"].startswith("GOLDEN")
    assert r["civil_war"].startswith("IMPOSSIBLE")
    assert r["fall"].startswith("NEVER")
    assert "NEVER STOPS" in r["status"]
