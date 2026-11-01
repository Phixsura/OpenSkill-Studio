from app.services.app_api_developer_platform_sdk_api_platform_api_api_response_compression_stats import AppAPIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStats

class TestResponseCompressionStats:
    def test_record(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStats()
        cs = s.record("inst-1", "/api/users", 10000, 3000, True)
        assert cs.savings_pct == 70.0
        assert cs.bandwidth_saved_bytes == 7000

    def test_total_savings(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStats()
        s.record("inst-1", "/a", 10000, 3000, True)
        s.record("inst-1", "/b", 5000, 2000, True)
        assert s.total_savings("inst-1") == 10000

    def test_best_savings(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStats()
        s.record("inst-1", "/a", 10000, 3000, True)  # 70%
        s.record("inst-1", "/b", 5000, 4500, True)   # 10%
        best = s.best_savings("inst-1", 1)
        assert best[0].endpoint == "/a"

    def test_isolation(self):
        s = AppAPIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStats()
        s.record("inst-1", "/api", 10000, 3000, True)
        assert s.total_savings("inst-2") == 0
