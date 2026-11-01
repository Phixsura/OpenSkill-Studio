from app.services.app_marketplace_app_app_app_trending import calculate_trending

def test_trending():
    apps = [
        {"id": "a1", "name": "SlowApp", "installs_current": 100, "installs_previous": 90, "rating": 4.0},
        {"id": "a2", "name": "FastApp", "installs_current": 500, "installs_previous": 100, "rating": 4.5},
        {"id": "a3", "name": "NewApp", "installs_current": 200, "installs_previous": 10, "rating": 4.8},
    ]
    r = calculate_trending(apps=apps)
    assert r["trending"][0]["name"] in ("FastApp", "NewApp")  # highest growth
    assert r["total_evaluated"] == 3
    assert r["trending"][0]["growth_pct"] > 100
