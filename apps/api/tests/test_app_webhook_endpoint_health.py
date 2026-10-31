from app.services.app_webhook_endpoint_health import record_delivery, get_endpoint_health, list_unhealthy_endpoints

def test_healthy():
    ep = "https://healthy.example.com/hook"
    for _ in range(100):
        record_delivery(ep, success=True, duration_ms=50)
    h = get_endpoint_health(ep)
    assert h["status"] == "healthy"
    assert h["success_rate"] == 100.0

def test_degraded():
    ep = "https://degraded.example.com/hook"
    for _ in range(85):
        record_delivery(ep, success=True, duration_ms=50)
    for _ in range(15):
        record_delivery(ep, success=False, duration_ms=5000)
    h = get_endpoint_health(ep)
    assert h["status"] == "degraded"

def test_unknown():
    h = get_endpoint_health("https://unknown.example.com")
    assert h["status"] == "unknown"

def test_avg_ms():
    ep = "https://avg.example.com/hook"
    record_delivery(ep, success=True, duration_ms=100)
    record_delivery(ep, success=True, duration_ms=200)
    assert get_endpoint_health(ep)["avg_ms"] == 150.0

def test_unhealthy_list():
    ep = "https://bad.example.com/hook"
    for _ in range(10):
        record_delivery(ep, success=False, duration_ms=5000)
    unhealthy = list_unhealthy_endpoints()
    assert any(u["endpoint"] == ep for u in unhealthy)
