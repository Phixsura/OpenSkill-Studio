from app.services.app_api_developer_platform_health import AppAPIDeveloperPlatformHealth

class TestHealth:
    def test_overall(self):
        h = AppAPIDeveloperPlatformHealth()
        ph = h.update("inst-1", api_health=90, webhook_health=95, documentation_health=80, developer_experience=85)
        assert ph.overall == 87.5
        assert ph.grade == "B"

    def test_a_plus(self):
        h = AppAPIDeveloperPlatformHealth()
        ph = h.update("inst-1", api_health=98, webhook_health=97, documentation_health=96, developer_experience=95)
        assert ph.grade == "A+"

    def test_isolation(self):
        h = AppAPIDeveloperPlatformHealth()
        h.update("inst-1", api_health=50)
        assert h.get("inst-2").overall == 100.0
