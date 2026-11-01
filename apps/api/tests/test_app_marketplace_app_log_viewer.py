from app.services.app_marketplace_app_log_viewer import parse_log_line, filter_logs

def test_parse():
    r = parse_log_line(line="[2026-10-23T12:00:00] [ERROR] Connection failed")
    assert r["parsed"]
    assert r["level"] == "error"
    assert "Connection failed" in r["message"]

def test_parse_invalid():
    r = parse_log_line(line="just a random line")
    assert not r["parsed"]

def test_filter_level():
    logs = [{"level": "debug", "message": "trace"}, {"level": "error", "message": "fail"},
            {"level": "info", "message": "ok"}]
    r = filter_logs(logs=logs, min_level="error")
    assert r["total_matched"] == 1
    assert r["logs"][0]["level"] == "error"

def test_filter_search():
    logs = [{"level": "info", "message": "User logged in"},
            {"level": "info", "message": "Payment processed"}]
    r = filter_logs(logs=logs, search="payment")
    assert r["total_matched"] == 1
