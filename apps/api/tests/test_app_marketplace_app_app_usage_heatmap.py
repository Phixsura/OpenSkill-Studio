from app.services.app_marketplace_app_app_usage_heatmap import build_heatmap

def test_heatmap():
    events = [
        {"timestamp": "2026-01-01T10:30:00Z"},
        {"timestamp": "2026-01-01T10:45:00Z"},
        {"timestamp": "2026-01-01T14:00:00Z"},
        {"timestamp": "2026-01-02T10:15:00Z"},
    ]
    r = build_heatmap(events=events)
    assert r["total_events"] == 4
    assert len(r["cells"]) == 168  # 7 * 24
    assert r["peak_count"] >= 2

def test_empty():
    r = build_heatmap(events=[])
    assert r["total_events"] == 0
