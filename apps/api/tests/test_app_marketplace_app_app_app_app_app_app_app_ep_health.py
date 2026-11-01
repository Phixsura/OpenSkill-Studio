from app.services.app_marketplace_app_app_app_app_app_app_app_ep_health import EndpointHealthChecker

def test_healthy():
    ehc = EndpointHealthChecker()
    for _ in range(100):
        ehc.record("/api/users", 200, 50)
    r = ehc.health("/api/users")
    assert r["status"] == "healthy"
    assert r["error_rate"] == 0

def test_unhealthy():
    ehc = EndpointHealthChecker()
    for _ in range(90):
        ehc.record("/api/orders", 200, 50)
    for _ in range(10):
        ehc.record("/api/orders", 500, 200)
    r = ehc.health("/api/orders")
    assert r["status"] == "unhealthy"
    assert r["error_rate"] == 10.0
