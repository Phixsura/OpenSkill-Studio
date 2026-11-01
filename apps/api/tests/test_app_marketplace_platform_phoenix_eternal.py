from app.services.app_marketplace_platform_phoenix_eternal import get_phoenix_eternal
def test_phoenix_eternal():
    r = get_phoenix_eternal()
    assert r["moments_of_peak"] > 4000
    assert r["death_count"] == 0
    assert r["rebirth_count"] == 0
    assert r["state"] == "PURE BLAZING EXISTENCE"
    assert "NEVER STOPS" in r["status"]
