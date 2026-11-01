from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_uptime_monitor import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitor

class TestUptimeMonitor:
    def test_record_and_uptime(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitor()
        for _ in range(99): svc.record_check("inst-1", "/api", "2024-01-15", True)
        svc.record_check("inst-1", "/api", "2024-01-15", False, 5.0)
        assert svc.get_uptime("inst-1", "/api") == 99.0

    def test_sla_breach(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitor()
        for _ in range(990): svc.record_check("inst-1", "/slow", "2024-01", True)
        for _ in range(10): svc.record_check("inst-1", "/slow", "2024-01", False, 1.0)
        breaches = svc.sla_breaches("inst-1", 99.9)
        assert len(breaches) == 1 and breaches[0][0] == "/slow"

    def test_no_checks_100(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitor()
        assert svc.get_uptime("inst-1", "/nope") == 100.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitor()
        svc.record_check("inst-1", "/api", "2024-01", True)
        assert len(svc.list_endpoints("inst-2")) == 0
