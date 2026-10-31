from app.services.app_marketplace_app_developer_app_webhook_analytics import compute_delivery_metrics, group_by_event_type, identify_failing_endpoints

def test_metrics():
    deliveries = [{"success": True, "latency_ms": 100}, {"success": True, "latency_ms": 200},
                  {"success": False, "latency_ms": 5000}]
    m = compute_delivery_metrics(deliveries=deliveries)
    assert m["total"] == 3
    assert m["failures"] == 1
    assert m["avg_latency_ms"] > 0

def test_empty():
    m = compute_delivery_metrics(deliveries=[])
    assert m["total"] == 0

def test_group():
    deliveries = [{"event_type": "install", "success": True, "latency_ms": 100},
                  {"event_type": "install", "success": True, "latency_ms": 200},
                  {"event_type": "update", "success": False, "latency_ms": 50}]
    g = group_by_event_type(deliveries=deliveries)
    assert g["unique_types"] == 2

def test_failing():
    deliveries = [{"url": "https://bad.com", "success": False}] * 8 + [{"url": "https://bad.com", "success": True}] * 2 + \
                 [{"url": "https://good.com", "success": True}] * 10
    r = identify_failing_endpoints(deliveries=deliveries, threshold=50)
    assert len(r) == 1
    assert r[0]["url"] == "https://bad.com"
