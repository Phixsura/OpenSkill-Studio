from app.services.app_api_platform_stats import AppAPIPlatformStats

class TestPlatformStats:
    def test_update(self):
        s = AppAPIPlatformStats()
        stats = s.update("inst-1", total_services=15, total_endpoints=120, total_api_calls=500000)
        assert stats.total_services == 15
        assert stats.total_api_calls == 500000

    def test_healthy(self):
        s = AppAPIPlatformStats()
        s.update("inst-1", overall_health=99.9, active_incidents=0)
        assert s.is_healthy("inst-1") is True

    def test_unhealthy(self):
        s = AppAPIPlatformStats()
        s.update("inst-1", overall_health=85.0, active_incidents=2)
        assert s.is_healthy("inst-1") is False

    def test_default(self):
        s = AppAPIPlatformStats()
        assert s.get_stats("inst-1").total_services == 0

    def test_isolation(self):
        s = AppAPIPlatformStats()
        s.update("inst-1", total_services=10)
        assert s.get_stats("inst-2").total_services == 0
