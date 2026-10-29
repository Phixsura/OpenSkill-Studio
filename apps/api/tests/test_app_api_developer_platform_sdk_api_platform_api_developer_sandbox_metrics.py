from app.services.app_api_developer_platform_sdk_api_platform_api_developer_sandbox_metrics import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetrics

class TestSandboxMetrics:
    def test_healthy(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetrics()
        s = m.update("inst-1", "sb1", total_requests=1000, errors=10)
        assert s.health == "healthy"
        assert s.error_rate == 1.0

    def test_unhealthy(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetrics()
        s = m.update("inst-1", "sb1", total_requests=100, errors=20)
        assert s.health == "unhealthy"

    def test_unhealthy_list(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetrics()
        m.update("inst-1", "sb1", total_requests=1000, errors=5)
        m.update("inst-1", "sb2", total_requests=100, errors=50)
        assert len(m.unhealthy("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetrics()
        m.update("inst-1", "sb1", total_requests=100)
        assert len(m.all_sandboxes("inst-2")) == 0
