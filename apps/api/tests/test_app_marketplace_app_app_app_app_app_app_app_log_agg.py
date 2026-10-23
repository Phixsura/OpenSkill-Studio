from app.services.app_marketplace_app_app_app_app_app_app_app_log_agg import aggregate_logs, find_patterns

def test_aggregate():
    r = aggregate_logs([
        {"name": "api", "logs": [{"level": "info"}, {"level": "error"}, {"level": "info"}]},
        {"name": "worker", "logs": [{"level": "warn"}, {"level": "error"}]},
    ])
    assert r["total_lines"] == 5
    assert r["error_count"] == 2
    assert r["by_source"]["api"] == 3

def test_patterns():
    logs = [{"message": "Connection timeout"}, {"message": "OK"}, {"message": "timeout again"}]
    r = find_patterns(logs, "timeout")
    assert r["matches"] == 2
    assert r["match_rate"] == 66.7
