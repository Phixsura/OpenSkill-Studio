from app.services.app_marketplace_app_app_app_app_app_app_app_usage_heatmap import build_heatmap, feature_adoption

def test_heatmap():
    events = [
        {"feature": "search", "hour": "09"}, {"feature": "search", "hour": "09"},
        {"feature": "search", "hour": "14"}, {"feature": "export", "hour": "10"},
    ]
    r = build_heatmap(events, ["search", "export"])
    assert r["total_events"] == 4
    assert r["hottest"]["feature"] == "search"
    assert r["hottest"]["hour"] == "09"

def test_adoption():
    events = [
        {"user_id": "u1", "feature": "search"},
        {"user_id": "u2", "feature": "search"},
        {"user_id": "u1", "feature": "export"},
        {"user_id": "u3", "feature": "dashboard"},
    ]
    r = feature_adoption(events, ["search", "export", "dashboard"])
    assert r["total_users"] == 3
    assert r["adoption"]["search"]["users"] == 2
    assert r["adoption"]["search"]["pct"] == 66.7
