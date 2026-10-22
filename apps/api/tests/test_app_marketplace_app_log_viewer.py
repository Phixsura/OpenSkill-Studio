from app.services.app_marketplace_app_log_viewer import filter_logs, aggregate_log_levels, format_log_entry

def test_filter_level():
    logs = [{"level": "error", "message": "fail"}, {"level": "info", "message": "ok"}]
    r = filter_logs(logs=logs, level="error")
    assert len(r) == 1

def test_filter_search():
    logs = [{"level": "info", "message": "User logged in"}, {"level": "info", "message": "Data saved"}]
    r = filter_logs(logs=logs, search="logged")
    assert len(r) == 1

def test_aggregate():
    logs = [{"level": "info"}, {"level": "error"}, {"level": "info"}, {"level": "error"}]
    r = aggregate_log_levels(logs=logs)
    assert r["counts"]["error"] == 2
    assert r["has_errors"]

def test_format():
    s = format_log_entry(entry={"timestamp": "2026-01-01T10:00:00Z", "level": "error", "message": "Connection failed"})
    assert "ERROR" in s
    assert "Connection failed" in s
