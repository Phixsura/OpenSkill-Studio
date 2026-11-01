from app.services.app_marketplace_extension_sandbox_api_analytics import (
    SandboxApiAnalyticsService,
)


def test_record_and_summary():
    svc = SandboxApiAnalyticsService()
    svc.record("sb-1", "GET", "/api/users", 50, 200)
    svc.record("sb-1", "GET", "/api/users", 70, 200)
    svc.record("sb-1", "POST", "/api/users", 100, 201)
    summary = svc.get_summary("sb-1")
    assert summary["total_hits"] == 3
    assert summary["total_endpoints"] == 2


def test_top_endpoints():
    svc = SandboxApiAnalyticsService()
    for _ in range(10):
        svc.record("sb-1", "GET", "/api/hot", 20, 200)
    for _ in range(3):
        svc.record("sb-1", "GET", "/api/cold", 20, 200)
    top = svc.get_top_endpoints("sb-1", 1)
    assert top[0]["endpoint"] == "/api/hot"
    assert top[0]["hits"] == 10


def test_slowest():
    svc = SandboxApiAnalyticsService()
    svc.record("sb-1", "GET", "/api/fast", 10, 200)
    svc.record("sb-1", "GET", "/api/slow", 500, 200)
    slowest = svc.get_slowest("sb-1", 1)
    assert slowest[0]["endpoint"] == "/api/slow"


def test_error_rate():
    svc = SandboxApiAnalyticsService()
    for _ in range(7):
        svc.record("sb-1", "GET", "/api/flaky", 20, 200)
    for _ in range(3):
        svc.record("sb-1", "GET", "/api/flaky", 20, 500)
    error_eps = svc.get_error_prone("sb-1")
    assert error_eps[0]["error_rate"] == 30.0


def test_top_consumers():
    svc = SandboxApiAnalyticsService()
    for _ in range(5):
        svc.record("sb-1", "GET", "/api", 10, 200, consumer="ext-a")
    for _ in range(3):
        svc.record("sb-1", "GET", "/api", 10, 200, consumer="ext-b")
    top = svc.get_top_consumers("sb-1")
    assert top[0]["consumer"] == "ext-a"
    assert top[0]["requests"] == 5


def test_empty_sandbox():
    svc = SandboxApiAnalyticsService()
    assert svc.get_summary("empty")["total_hits"] == 0
    assert svc.get_top_endpoints("empty") == []
