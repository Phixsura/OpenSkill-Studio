from app.services.app_marketplace_app_app_app_app_log_stream import build_log_stream

LOGS = [
    {"level": "debug", "message": "Loading config", "timestamp": "2026-01-01T10:00:00Z"},
    {"level": "info", "message": "Server started on port 3000", "timestamp": "2026-01-01T10:00:01Z"},
    {"level": "error", "message": "Connection refused to DB", "timestamp": "2026-01-01T10:00:05Z"},
    {"level": "warn", "message": "High memory usage", "timestamp": "2026-01-01T10:00:10Z"},
]

def test_filter_level():
    r = build_log_stream(logs=LOGS, min_level="warn")
    assert r["total"] == 2
    assert r["has_errors"]

def test_search():
    r = build_log_stream(logs=LOGS, search="connection")
    assert r["total"] == 1
    assert r["logs"][0]["level"] == "error"

def test_all():
    r = build_log_stream(logs=LOGS, min_level="debug")
    assert r["total"] == 4
