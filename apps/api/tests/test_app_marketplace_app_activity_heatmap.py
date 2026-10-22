from app.services.app_marketplace_app_activity_heatmap import build_heatmap, find_peak_hours

def test_heatmap():
    events = [
        {"timestamp": "2026-01-01T10:30:00Z"}, {"timestamp": "2026-01-01T10:45:00Z"},
        {"timestamp": "2026-01-01T14:00:00Z"}, {"timestamp": "2026-01-02T10:00:00Z"},
    ]
    h = build_heatmap(events=events)
    assert h["total_events"] == 4
    assert len(h["rows"]) == 2

def test_peak():
    heatmap = {"rows": [{"hours": {"10": 50, "14": 30, "3": 5}}]}
    peaks = find_peak_hours(heatmap=heatmap)
    assert peaks[0]["hour"] == 10
