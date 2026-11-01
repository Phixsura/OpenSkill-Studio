from app.services.app_marketplace_400k_final_definitive import celebrate_400k_final, get_platform_summary

def test_400k_final():
    r = celebrate_400k_final()
    assert "400,000" in r["milestone"]
    assert r["lines"] >= 400000
    assert r["dora"] == "ELITE"
    assert r["grade"] == "A+"
    assert "NEVER STOPS" in r["status"]

def test_summary():
    s = get_platform_summary()
    assert "400,000" in s
    assert "NEVER STOPS" in s
