from app.services.app_api_developer_platform_sdk_api_endpoint_traffic_analyzer import AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer

class TestEndpointTrafficAnalyzer:
    def test_record(self):
        a = AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer()
        t = a.record("inst-1", "/api/users", "GET", 500000, 200, peak_rps=500)
        assert t.traffic_tier == "high"

    def test_mega(self):
        a = AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer()
        t = a.record("inst-1", "/api/health", "GET", 5000000, 1)
        assert t.traffic_tier == "mega"

    def test_hottest(self):
        a = AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer()
        a.record("inst-1", "/a", "GET", 100, 10)
        a.record("inst-1", "/b", "GET", 50000, 50)
        assert a.hottest("inst-1", 1)[0].endpoint == "/b"

    def test_by_tier(self):
        a = AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer()
        a.record("inst-1", "/a", "GET", 5000000, 1)
        a.record("inst-1", "/b", "GET", 100, 1)
        tiers = a.by_tier("inst-1")
        assert "mega" in tiers
        assert "low" in tiers

    def test_isolation(self):
        a = AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer()
        a.record("inst-1", "/a", "GET", 100, 10)
        assert len(a.all_traffic("inst-2")) == 0
