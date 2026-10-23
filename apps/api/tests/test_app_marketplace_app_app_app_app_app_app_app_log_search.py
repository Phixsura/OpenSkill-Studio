from app.services.app_marketplace_app_app_app_app_app_app_app_log_search import search_logs, parse_log_line

def test_search():
    logs = [
        {"level": "error", "service": "api", "message": "Connection timeout to database"},
        {"level": "info", "service": "api", "message": "Request processed in 45ms"},
        {"level": "error", "service": "worker", "message": "Job failed: timeout"},
        {"level": "warn", "service": "api", "message": "Slow query detected"},
    ]
    r = search_logs(logs, query="timeout")
    assert r["total"] == 2
    r2 = search_logs(logs, query="timeout", service="api")
    assert r2["total"] == 1
    r3 = search_logs(logs, query="", level="error")
    assert r3["total"] == 2

def test_parse():
    p = parse_log_line("[ERROR] api Connection refused")
    assert p["level"] == "error"
    assert p["service"] == "api"
    assert "Connection" in p["message"]
