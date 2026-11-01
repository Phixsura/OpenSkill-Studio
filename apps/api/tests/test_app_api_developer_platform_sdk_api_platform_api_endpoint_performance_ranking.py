from app.services.app_api_developer_platform_sdk_api_platform_api_endpoint_performance_ranking import AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking

class TestEndpointPerformanceRanking:
    def test_fast(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking()
        e = r.record("inst-1", "/api/users", 30, 150, 0.1, 10000)
        assert "Fast" in e.rank_label
        assert e.performance_score >= 90

    def test_poor(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking()
        e = r.record("inst-1", "/api/heavy", 500, 3000, 10, 50)
        assert "Poor" in e.rank_label

    def test_ranked(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking()
        r.record("inst-1", "/fast", 30, 100, 0.1, 10000)
        r.record("inst-1", "/slow", 500, 3000, 10, 50)
        ranked = r.ranked("inst-1")
        assert ranked[0].endpoint == "/fast"

    def test_slowest(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking()
        r.record("inst-1", "/fast", 30, 100, 0.1, 10000)
        r.record("inst-1", "/slow", 500, 3000, 10, 50)
        assert r.slowest("inst-1", 1)[0].endpoint == "/slow"

    def test_isolation(self):
        r = AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking()
        r.record("inst-1", "/api", 50, 200, 0.5, 5000)
        assert len(r.all_endpoints("inst-2")) == 0
