from app.services.app_marketplace_app_developer_api_usage_heatmap import build_usage_heatmap, find_quiet_hours

def test_heatmap():
    calls = [{"timestamp": "2026-01-01T10:30:00Z", "day_of_week": 0},
             {"timestamp": "2026-01-01T10:45:00Z", "day_of_week": 0},
             {"timestamp": "2026-01-02T14:00:00Z", "day_of_week": 1}]
    h = build_usage_heatmap(api_calls=calls)
    assert h["total_calls"] == 3
    assert len(h["rows"]) == 7

def test_quiet():
    heatmap = {"total_calls": 100, "rows": [{"hours": [0]*10 + [50] + [0]*13}] + [{"hours": [0]*24}]*6}
    quiet = find_quiet_hours(heatmap=heatmap)
    assert 10 not in quiet  # hour 10 is busy
