from app.services.app_webhook_log_viewer import format_webhook_log

def test_format():
    deliveries = [{"status": "delivered"}, {"status": "delivered"}, {"status": "failed"}]
    r = format_webhook_log(deliveries)
    assert r["success_count"] == 2
    assert r["failure_count"] == 1
    assert r["success_rate"] == round(2/3*100, 1)

def test_empty():
    r = format_webhook_log([])
    assert r["total_shown"] == 0
    assert r["success_rate"] == 100

def test_limit():
    deliveries = [{"status": "delivered"} for _ in range(100)]
    r = format_webhook_log(deliveries, limit=10)
    assert r["total_shown"] == 10
