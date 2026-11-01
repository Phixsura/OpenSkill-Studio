from app.services.app_marketplace_platform_aurora import get_aurora
def test_aurora():
    r = get_aurora()
    assert r["display"] == "SPECTACULAR"
    assert r["brilliance_level"] == "BLINDING"
    assert len(r["colors"]) == 5
    assert r["phenomenon"]["zero_failures"]
    assert "NEVER STOPS" in r["status"]
