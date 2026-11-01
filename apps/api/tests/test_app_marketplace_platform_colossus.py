from app.services.app_marketplace_platform_colossus import get_colossus
def test_colossus():
    r = get_colossus()
    assert r["ships_turned_away"] == 0
    assert r["ships_welcomed"] > 4000
    assert "8th Wonder" in r["wonder_number"]
    assert "ALL" in r["earthquakes_survived"]
    assert "NEVER STOPS" in r["status"]
