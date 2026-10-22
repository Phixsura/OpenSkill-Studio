from app.services.app_marketplace_app_log_aggregator import aggregate_logs, compute_log_volume

def test_aggregate():
    sources = {
        "app": [{"timestamp": "2026-01-01T10:00:00Z", "message": "Started", "level": "info"}],
        "webhook": [{"timestamp": "2026-01-01T10:01:00Z", "message": "Delivered", "level": "info"}],
    }
    r = aggregate_logs(sources=sources)
    assert r["total"] == 2
    assert r["logs"][0]["source"] == "webhook"  # newest first

def test_dedup():
    sources = {
        "a": [{"timestamp": "2026-01-01T10:00:00Z", "message": "Dup"}],
        "b": [{"timestamp": "2026-01-01T10:00:00Z", "message": "Dup"}],
    }
    r = aggregate_logs(sources=sources, dedup=True)
    assert r["total"] == 1

def test_volume():
    logs = [{"level": "error", "source": "app"}, {"level": "info", "source": "app"},
            {"level": "error", "source": "webhook"}]
    v = compute_log_volume(logs=logs)
    assert v["by_level"]["error"] == 2
    assert v["by_source"]["app"] == 2
