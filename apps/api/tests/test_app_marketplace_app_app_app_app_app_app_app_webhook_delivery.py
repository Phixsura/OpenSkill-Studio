from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_delivery import record_delivery, summarize_deliveries

def test_record():
    d = record_delivery("https://example.com/hook", "app.installed", 200, 150, 1024)
    assert d["success"]
    assert d["response_ms"] == 150
    assert "&" not in d["endpoint"] or "amp;" in d["endpoint"]

def test_summarize():
    deliveries = [
        record_delivery("https://a.com", "install", 200, 100),
        record_delivery("https://a.com", "install", 200, 200),
        record_delivery("https://a.com", "uninstall", 500, 3000),
    ]
    r = summarize_deliveries(deliveries)
    assert r["total"] == 3
    assert r["successes"] == 2
    assert r["success_rate"] == 67
    assert r["avg_response_ms"] == 1100
    assert r["by_event"]["install"] == 2
