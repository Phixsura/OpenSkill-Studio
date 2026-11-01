from app.services.app_marketplace_app_activity_heatmap import build_activity_heatmap

def test_heatmap():
    events = [
        {"day_of_week": "Mon", "hour": 9},
        {"day_of_week": "Mon", "hour": 9},
        {"day_of_week": "Mon", "hour": 10},
        {"day_of_week": "Fri", "hour": 14},
    ]
    r = build_activity_heatmap(events=events)
    assert r["total_events"] == 4
    assert r["peak"]["day"] == "Mon"
    assert r["peak"]["hour"] == 9
    assert r["peak"]["count"] == 2
    assert len(r["cells"]) == 7 * 24

def test_empty():
    r = build_activity_heatmap(events=[])
    assert r["total_events"] == 0
