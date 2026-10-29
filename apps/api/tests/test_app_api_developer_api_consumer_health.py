from app.services.app_api_developer_api_consumer_health import AppAPIDeveloperAPIConsumerHealth

class TestConsumerHealth:
    def test_healthy(self):
        h = AppAPIDeveloperAPIConsumerHealth()
        ch = h.update("inst-1", "app-1", 1.0, 5000)
        assert ch.status == "healthy"

    def test_degraded(self):
        h = AppAPIDeveloperAPIConsumerHealth()
        ch = h.update("inst-1", "app-1", 15.0, 1000)
        assert ch.status == "degraded"

    def test_unhealthy_list(self):
        h = AppAPIDeveloperAPIConsumerHealth()
        h.update("inst-1", "app-1", 1, 5000)
        h.update("inst-1", "app-2", 20, 100)
        assert len(h.unhealthy("inst-1")) == 1

    def test_isolation(self):
        h = AppAPIDeveloperAPIConsumerHealth()
        h.update("inst-1", "app-1", 1, 100)
        assert h.list_all("inst-2") == []
