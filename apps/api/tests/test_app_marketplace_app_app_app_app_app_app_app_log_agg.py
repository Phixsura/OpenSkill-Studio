from app.services.app_marketplace_app_app_app_app_app_app_app_log_agg import aggregate_logs, extract_patterns

def test_aggregate():
    r = aggregate_logs([
        {"level": "info", "source": "api", "message": "ok"},
        {"level": "error", "source": "api", "message": "fail"},
        {"level": "info", "source": "worker", "message": "done"},
    ])
    assert r["total"] == 3
    assert r["error_count"] == 1
    assert r["has_errors"]
    assert r["top_sources"][0]["source"] == "api"

def test_patterns():
    r = extract_patterns([
        {"message": "timeout: svc-a"},
        {"message": "timeout: svc-b"},
        {"message": "success: done"},
    ], min_count=2)
    assert len(r) == 1
    assert r[0]["pattern"] == "timeout"
