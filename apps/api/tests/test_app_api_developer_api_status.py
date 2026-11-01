from app.services.app_api_developer_api_status import AppAPIDeveloperAPIStatus

class TestStatus:
    def test_operational(self):
        s = AppAPIDeveloperAPIStatus()
        s.update("inst-1", "API", "operational", 50)
        s.update("inst-1", "DB", "operational", 10)
        assert s.overall_status("inst-1") == "operational"

    def test_degraded(self):
        s = AppAPIDeveloperAPIStatus()
        s.update("inst-1", "API", "operational")
        s.update("inst-1", "DB", "degraded")
        assert s.overall_status("inst-1") == "degraded"

    def test_outage(self):
        s = AppAPIDeveloperAPIStatus()
        s.update("inst-1", "API", "outage")
        assert s.overall_status("inst-1") == "outage"

    def test_isolation(self):
        s = AppAPIDeveloperAPIStatus()
        s.update("inst-1", "API", "outage")
        assert s.overall_status("inst-2") == "operational"
