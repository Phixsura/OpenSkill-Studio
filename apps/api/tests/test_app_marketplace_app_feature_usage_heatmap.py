from app.services.app_marketplace_app_feature_usage_heatmap import build_usage_heatmap

def test_heatmap():
    features = [
        {"name": "Search", "category": "core", "daily_usage": [100, 120, 130, 140, 150, 160, 170]},
        {"name": "Export", "category": "tools", "daily_usage": [10, 12, 8, 11, 9, 10, 7]},
        {"name": "Settings", "category": "config", "daily_usage": [5, 5, 5, 5, 5, 5, 5]},
    ]
    r = build_usage_heatmap(features=features, days=7)
    assert r["most_used"] == "Search"
    assert r["least_used"] == "Settings"
    assert r["features"][0]["trend"] == "up"
    assert r["total_features"] == 3

def test_empty():
    r = build_usage_heatmap(features=[], days=7)
    assert r["most_used"] is None
    assert r["total_features"] == 0
