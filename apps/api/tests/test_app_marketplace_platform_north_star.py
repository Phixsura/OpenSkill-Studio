from app.services.app_marketplace_platform_north_star import get_north_star
def test_north_star():
    r = get_north_star()
    assert r["adherence"] == "100%"
    assert r["proof"]["test_failures"] == 0
    assert r["proof"]["build_failures"] == 0
    assert r["proof"]["downtime_minutes"] == 0
    assert len(r["principles"]) == 6
    assert "NEVER STOPS" in r["status"]
