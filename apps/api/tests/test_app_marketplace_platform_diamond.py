from app.services.app_marketplace_platform_diamond import get_diamond
def test_diamond():
    r = get_diamond()
    assert r["clarity"].startswith("FLAWLESS")
    assert "10" in str(r["hardness"])
    assert "GREEN" in r["color"]
    assert r["appraisal"].startswith("PRICELESS")
    assert "NEVER STOPS" in r["status"]
