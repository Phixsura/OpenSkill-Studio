from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_platform_summary import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummary, PlatformSummary,
)

class TestPlatformSummary:
    def test_healthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummary()
        svc.update("inst-1", PlatformSummary(total_consumers=50, active_consumers=45, error_rate_24h=1.0, uptime_30d=99.99))
        assert svc.is_healthy("inst-1") is True

    def test_critical(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummary()
        svc.update("inst-1", PlatformSummary(active_incidents=2, error_rate_24h=15))
        assert svc.get_summary("inst-1").health_status == "critical"

    def test_needs_attention(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummary()
        svc.update("inst-1", PlatformSummary(active_incidents=1, open_tickets=15, total_endpoints=10, documented_endpoints=5))
        issues = svc.needs_attention("inst-1")
        assert len(issues) >= 2

    def test_doc_coverage(self):
        s = PlatformSummary(total_endpoints=20, documented_endpoints=15)
        assert s.doc_coverage_pct == 75.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummary()
        svc.update("inst-1", PlatformSummary(total_consumers=10))
        assert svc.get_summary("inst-2").total_consumers == 0
