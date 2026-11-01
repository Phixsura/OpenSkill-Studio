from app.services.app_marketplace_app_app_app_app_app_app_app_structured_log import format_log, parse_log_line, aggregate_log_levels

def test_format():
    r = format_log("info", "Server started", {"port": 8080}, "api", "trace-123")
    assert r["level"] == "INFO"
    assert r["service"] == "api"
    assert "[INFO]" in r["formatted"]

def test_parse():
    r = parse_log_line("[ERROR] Connection failed to database")
    assert r["parsed"]
    assert r["level"] == "ERROR"

def test_aggregate():
    logs = [{"level": "INFO"}, {"level": "INFO"}, {"level": "ERROR"}, {"level": "WARN"}]
    r = aggregate_log_levels(logs)
    assert r["total"] == 4
    assert r["error_pct"] == 25.0
