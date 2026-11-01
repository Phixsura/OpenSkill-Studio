from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_request_rate_monitor import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitor

class TestRequestRateMonitor:
    def test_record(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitor()
        r = m.record("inst-1", "/api/users", 500)
        assert r.current_rps == 500

    def test_spike_detection(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitor()
        for _ in range(10): m.record("inst-1", "/api", 100)
        m.record("inst-1", "/api", 500)  # 5x avg
        assert m.all_rates("inst-1")[0].load_level == "spike"

    def test_peak(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitor()
        m.record("inst-1", "/api", 100)
        m.record("inst-1", "/api", 500)
        m.record("inst-1", "/api", 200)
        assert m.all_rates("inst-1")[0].peak_rps == 500

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitor()
        m.record("inst-1", "/api", 100)
        assert len(m.all_rates("inst-2")) == 0
