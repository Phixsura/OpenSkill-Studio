from app.services.app_marketplace_extension_sandbox_api_rate_window import (
    SandboxApiRateWindowService,
)


def test_configure_and_check():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api/data", 60, 100)
    result = svc.check("sb-1", "/api/data")
    assert result["allowed"] is True
    assert result["remaining"] == 99


def test_rate_limit_exceeded():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api", 60, 3)
    for _ in range(3):
        svc.check("sb-1", "/api")
    result = svc.check("sb-1", "/api")
    assert result["allowed"] is False
    assert result["remaining"] == 0
    assert "Retry-After" in result["headers"]


def test_burst_allowance():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api", 60, 3, burst=2)
    for _ in range(5):
        r = svc.check("sb-1", "/api")
        assert r["allowed"] is True
    # 6th should fail
    result = svc.check("sb-1", "/api")
    assert result["allowed"] is False


def test_headers():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api", 60, 100)
    result = svc.check("sb-1", "/api")
    assert result["headers"]["X-RateLimit-Limit"] == "100"
    assert result["headers"]["X-RateLimit-Remaining"] == "99"


def test_no_config_allows():
    svc = SandboxApiRateWindowService()
    result = svc.check("sb-1", "/unknown")
    assert result["allowed"] is True


def test_usage():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api", 60, 100)
    for _ in range(25):
        svc.check("sb-1", "/api")
    usage = svc.get_usage("sb-1", "/api")
    assert usage["current"] == 25
    assert usage["usage_percent"] == 25.0


def test_reset():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api", 60, 5)
    for _ in range(5):
        svc.check("sb-1", "/api")
    svc.reset("sb-1", "/api")
    result = svc.check("sb-1", "/api")
    assert result["allowed"] is True
    assert result["remaining"] == 4


def test_list_endpoints():
    svc = SandboxApiRateWindowService()
    svc.configure("sb-1", "/api/a", 60, 10)
    svc.configure("sb-1", "/api/b", 60, 20)
    assert svc.list_endpoints("sb-1") == ["/api/a", "/api/b"]
