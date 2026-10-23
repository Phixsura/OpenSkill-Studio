from app.services.app_marketplace_app_app_app_app_app_app_app_feature_heatmap import build_heatmap, top_features

def test_heatmap():
    events = [
        {"feature": "search", "hour": 9}, {"feature": "search", "hour": 10},
        {"feature": "search", "hour": 10}, {"feature": "dashboard", "hour": 9},
        {"feature": "dashboard", "hour": 14}, {"feature": "settings", "hour": 16},
    ]
    r = build_heatmap(events)
    assert r["total_features"] == 3
    assert r["total_events"] == 6
    search_row = next(f for f in r["features"] if f["feature"] == "search")
    assert search_row["total"] == 3
    assert search_row["peak_hour"] == 10

def test_top():
    events = [{"feature": "a"}] * 10 + [{"feature": "b"}] * 5 + [{"feature": "c"}] * 3
    t = top_features(events, limit=2)
    assert len(t) == 2
    assert t[0]["feature"] == "a"
    assert t[0]["pct"] > 50
