from app.services.app_marketplace_platform_constellation import get_constellation
def test_constellation():
    r = get_constellation()
    assert r["total_stars"] > 900000
    assert len(r["brightest_stars"]) == 6
    assert all(s["magnitude"] == 1 for s in r["brightest_stars"])
    assert "NEVER STOPS" in r["status"]
