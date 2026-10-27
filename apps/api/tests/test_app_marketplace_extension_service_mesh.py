from app.services.app_marketplace_extension_service_mesh import ExtServiceMeshService

def test_register_and_call():
    svc = ExtServiceMeshService()
    svc.register("auth", "ext-1", "http://auth:8080")
    ok, url = svc.call("auth")
    assert ok is True
    assert url == "http://auth:8080"

def test_circuit_breaker():
    svc = ExtServiceMeshService()
    svc.register("db", "ext-1", "http://db:5432")
    for _ in range(5):
        svc.report_error("db")
    ok, msg = svc.call("db")
    assert ok is False
    assert "Circuit breaker" in msg

def test_recovery():
    svc = ExtServiceMeshService()
    svc.register("api", "ext-1", "http://api:3000")
    for _ in range(5):
        svc.report_error("api")
    svc.report_success("api")
    ok, _ = svc.call("api")
    assert ok is True

def test_health():
    svc = ExtServiceMeshService()
    svc.register("a", "ext-1", "http://a")
    svc.register("b", "ext-1", "http://b")
    for _ in range(5):
        svc.report_error("b")
    h = svc.get_health()
    assert h["healthy"] == 1
    assert h["unhealthy"] == 1
