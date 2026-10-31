from app.services.app_api_developer_platform_sdk_api_endpoint_error_rate_monitor import AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor

class TestEndpointErrorRateMonitor:
    def test_record(self):
        m = AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor()
        for _ in range(90): m.record("inst-1", "/api/users", True)
        for _ in range(10): m.record("inst-1", "/api/users", False, "TIMEOUT")
        r = m.all_endpoints("inst-1")[0]
        assert r.error_rate_pct == 10.0
        assert r.status == "critical"

    def test_normal(self):
        m = AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor()
        for _ in range(1000): m.record("inst-1", "/api", True)
        assert m.all_endpoints("inst-1")[0].status == "normal"

    def test_critical_endpoints(self):
        m = AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor()
        for _ in range(50): m.record("inst-1", "/bad", False, "ERR")
        for _ in range(50): m.record("inst-1", "/bad", True)
        for _ in range(100): m.record("inst-1", "/good", True)
        assert len(m.critical_endpoints("inst-1")) == 1

    def test_overall(self):
        m = AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor()
        for _ in range(95): m.record("inst-1", "/api", True)
        for _ in range(5): m.record("inst-1", "/api", False)
        assert m.overall_error_rate("inst-1") == 5.0

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiEndpointErrorRateMonitor()
        m.record("inst-1", "/api", True)
        assert m.overall_error_rate("inst-2") == 0.0
