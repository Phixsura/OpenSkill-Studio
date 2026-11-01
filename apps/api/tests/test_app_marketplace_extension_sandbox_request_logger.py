from app.services.app_marketplace_extension_sandbox_request_logger import SandboxRequestLoggerService

def test_log_and_query():
    svc = SandboxRequestLoggerService()
    svc.log("sb-1", "GET", "/api/data", 200, 45)
    svc.log("sb-1", "POST", "/api/data", 201, 80)
    entries = svc.query("sb-1")
    assert len(entries) == 2

def test_filter_method():
    svc = SandboxRequestLoggerService()
    svc.log("sb-1", "GET", "/a", 200, 10)
    svc.log("sb-1", "POST", "/b", 201, 20)
    assert len(svc.query("sb-1", method="GET")) == 1

def test_filter_errors():
    svc = SandboxRequestLoggerService()
    svc.log("sb-1", "GET", "/ok", 200, 10)
    svc.log("sb-1", "GET", "/err", 500, 100)
    assert len(svc.query("sb-1", min_status=400)) == 1

def test_stats():
    svc = SandboxRequestLoggerService()
    svc.log("sb-1", "GET", "/a", 200, 50)
    svc.log("sb-1", "GET", "/b", 500, 100)
    stats = svc.get_stats("sb-1")
    assert stats["total"] == 2
    assert stats["error_count"] == 1
    assert stats["avg_latency"] == 75.0
