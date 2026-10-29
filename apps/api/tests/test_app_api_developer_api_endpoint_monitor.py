from app.services.app_api_developer_api_endpoint_monitor import AppAPIDeveloperAPIEndpointMonitor

class TestMonitor:
    def test_healthy(self):
        m = AppAPIDeveloperAPIEndpointMonitor()
        s = m.update("inst-1", "GET", "/api/users", 50, 0.5, 100)
        assert s.status == "healthy"

    def test_slow(self):
        m = AppAPIDeveloperAPIEndpointMonitor()
        s = m.update("inst-1", "GET", "/api/search", 1500, 1.0, 50)
        assert s.status == "slow"

    def test_down(self):
        m = AppAPIDeveloperAPIEndpointMonitor()
        s = m.update("inst-1", "POST", "/api/auth", 200, 15.0, 10)
        assert s.status == "down"

    def test_unhealthy(self):
        m = AppAPIDeveloperAPIEndpointMonitor()
        m.update("inst-1", "GET", "/fast", 50, 0.5, 100)
        m.update("inst-1", "GET", "/slow", 2000, 1.0, 10)
        assert len(m.unhealthy("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIEndpointMonitor()
        m.update("inst-1", "GET", "/api", 50, 0, 100)
        assert m.list_monitors("inst-2") == []
