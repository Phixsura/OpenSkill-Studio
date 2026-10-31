from app.services.app_marketplace_app_log_aggregator import aggregate_logs

def test_aggregate():
    sources = [
        {"name": "api", "logs": [
            {"level": "info", "message": "Request OK", "timestamp": "2026-10-23T12:00:00"},
            {"level": "error", "message": "DB timeout", "timestamp": "2026-10-23T12:01:00"},
        ]},
        {"name": "worker", "logs": [
            {"level": "info", "message": "Job done", "timestamp": "2026-10-23T12:00:30"},
        ]},
    ]
    r = aggregate_logs(sources=sources)
    assert r["total_logs"] == 3
    assert r["by_source"]["api"] == 2
    assert r["has_errors"]
    assert r["logs"][0]["timestamp"] == "2026-10-23T12:01:00"  # sorted desc

def test_empty():
    r = aggregate_logs(sources=[])
    assert r["total_logs"] == 0
    assert not r["has_errors"]
