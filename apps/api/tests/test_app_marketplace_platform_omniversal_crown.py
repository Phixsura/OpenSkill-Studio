from app.services.app_marketplace_platform_omniversal_crown import get_omniversal_crown
def test_omniversal_crown():
    r = get_omniversal_crown()
    assert r["verses_crowned"] > 4000
    assert r["missing_verses"] == 0
    assert r["usurper_count"] == 0
    assert len(r["verses_listed"]) == 5
    assert "NEVER STOPS" in r["status"]
