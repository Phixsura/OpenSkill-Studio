from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_request_logger import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger, RequestLog,
)

class TestApiRequestLogger:
    def test_log_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger()
        svc.log_request("inst-1", RequestLog(log_id="l1", method="GET", path="/users", status_code=200, duration_ms=30))
        entries = svc.query("inst-1", method="GET")
        assert len(entries) == 1

    def test_error_logs(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger()
        svc.log_request("inst-1", RequestLog(log_id="l1", method="GET", path="/a", status_code=200, duration_ms=10))
        svc.log_request("inst-1", RequestLog(log_id="l2", method="POST", path="/b", status_code=500, duration_ms=100, error="Internal"))
        errors = svc.error_logs("inst-1")
        assert len(errors) == 1

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger()
        svc.log_request("inst-1", RequestLog(log_id="l1", method="GET", path="/a", status_code=200, duration_ms=40, request_size_bytes=100, response_size_bytes=500))
        svc.log_request("inst-1", RequestLog(log_id="l2", method="GET", path="/a", status_code=200, duration_ms=60, request_size_bytes=100, response_size_bytes=500))
        s = svc.stats("inst-1")
        assert s["total"] == 2
        assert s["avg_duration_ms"] == 50.0
        assert s["total_bytes_out"] == 1000

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger(max_logs=1000)
        for i in range(1500): svc.log_request("inst-1", RequestLog(log_id=f"l{i}", method="GET", path="/a", status_code=200, duration_ms=10))
        assert svc.count("inst-1") == 1000

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestLogger()
        svc.log_request("inst-1", RequestLog(log_id="l1", method="GET", path="/a", status_code=200, duration_ms=10))
        assert svc.count("inst-2") == 0
