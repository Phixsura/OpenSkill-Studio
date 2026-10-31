from app.services.app_marketplace_app_app_app_app_app_app_app_delivery_stats import compute_delivery_stats

def test_stats():
    deliveries = [
        {"success": True, "status_code": 200, "latency_ms": 150, "retries": 0},
        {"success": True, "status_code": 200, "latency_ms": 200, "retries": 0},
        {"success": False, "status_code": 500, "latency_ms": 3000, "retries": 2},
        {"success": True, "status_code": 200, "latency_ms": 100, "retries": 0},
    ]
    r = compute_delivery_stats(deliveries)
    assert r["total"] == 4
    assert r["success"] == 3
    assert r["success_rate"] == 75.0
    assert r["health"] == "poor"
    assert r["retry_count"] == 2
    assert r["by_status"][200] == 3
