from app.services.app_marketplace_app_app_app_app_app_app_app_log_search import search_logs, extract_services

def test_search():
    logs = [
        {"level": "error", "service": "api", "message": "Connection timeout"},
        {"level": "info", "service": "api", "message": "Request handled"},
        {"level": "error", "service": "worker", "message": "Task failed"},
    ]
    r = search_logs(logs, query="timeout")
    assert r["matched"] == 1
    assert r["results"][0]["message"] == "Connection timeout"
    r2 = search_logs(logs, level="error")
    assert r2["matched"] == 2

def test_services():
    logs = [{"service": "api"}, {"service": "worker"}, {"service": "api"}]
    assert extract_services(logs) == ["api", "worker"]
