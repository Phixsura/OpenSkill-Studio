from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_latency_percentile import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentile

class TestApiLatencyPercentile:
    def test_record_and_percentiles(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentile()
        for i in range(100): svc.record("inst-1", "/api", "GET", float(i))
        p = svc.get_percentiles("inst-1", "/api", "GET")
        assert p["p50"] == 50.0
        assert p["p99"] == 99.0
        assert p["count"] == 100

    def test_slow_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentile()
        for i in range(100): svc.record("inst-1", "/slow", "GET", 500.0 + i * 20)
        slow = svc.slow_endpoints("inst-1", p99_threshold_ms=1000)
        assert len(slow) == 1 and slow[0]["endpoint"] == "/slow"

    def test_no_data(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentile()
        p = svc.get_percentiles("inst-1", "/nope", "GET")
        assert p["count"] == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentile()
        svc.record("inst-1", "/api", "GET", 10.0)
        assert len(svc.list_endpoints("inst-2")) == 0
