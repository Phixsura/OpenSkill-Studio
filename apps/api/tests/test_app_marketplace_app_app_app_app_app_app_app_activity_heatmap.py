from app.services.app_marketplace_app_app_app_app_app_app_app_activity_heatmap import build_activity_heatmap

def test_heatmap():
    events = [
        {"day": 0, "hour": 9}, {"day": 0, "hour": 9}, {"day": 0, "hour": 10},
        {"day": 4, "hour": 14}, {"day": 4, "hour": 14}, {"day": 4, "hour": 14},
    ]
    r = build_activity_heatmap(events)
    assert r["total_events"] == 6
    assert r["peak"]["day"] == "Fri"
    assert r["peak"]["hour"] == 14
    assert r["peak"]["count"] == 3
    assert r["grid"][0]["total"] == 3  # Monday
