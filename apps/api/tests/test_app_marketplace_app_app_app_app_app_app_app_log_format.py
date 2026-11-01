from app.services.app_marketplace_app_app_app_app_app_app_app_log_format import format_log, parse_log_line, log_stats

def test_format():
    r = format_log("info", "Request handled", "api", {"status": 200})
    assert r["level"] == "INFO"
    assert r["service"] == "api"
    assert r["extra"]["status"] == 200

def test_parse():
    r = parse_log_line("2026-10-24T12:00:00Z [INFO] Request handled")
    assert r["parsed"]
    assert r["level"] == "INFO"

def test_stats():
    logs = [{"level": "INFO", "service": "api"}, {"level": "ERROR", "service": "api"},
            {"level": "INFO", "service": "worker"}]
    r = log_stats(logs)
    assert r["by_level"]["INFO"] == 2
    assert r["by_service"]["api"] == 2
