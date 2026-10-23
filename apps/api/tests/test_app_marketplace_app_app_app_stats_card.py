from app.services.app_marketplace_app_app_app_stats_card import build_app_stats_card

def test_stats():
    r = build_app_stats_card(app={"name": "MyApp", "installs": 25000, "active_users": 15000, "rating": 4.5})
    assert r["name"] == "MyApp"
    assert len(r["metrics"]) == 4
    assert r["metrics"][0]["display"] == "25.0K"
    assert r["health"] == "good"

def test_poor():
    r = build_app_stats_card(app={"name": "X", "installs": 100, "active_users": 5, "rating": 2.0})
    assert r["health"] == "poor"
