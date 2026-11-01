from app.services.app_api_developer_api_system_status import AppAPIDeveloperAPISystemStatus

class TestSystemStatus:
    def test_operational(self):
        s = AppAPIDeveloperAPISystemStatus()
        ss = s.set_status("inst-1", [{"name": "API", "status": "operational"}, {"name": "DB", "status": "operational"}])
        assert ss.overall == "all_systems_operational"

    def test_outage(self):
        s = AppAPIDeveloperAPISystemStatus()
        ss = s.set_status("inst-1", [{"name": "API", "status": "operational"}, {"name": "DB", "status": "outage"}])
        assert ss.overall == "major_outage"

    def test_degraded(self):
        s = AppAPIDeveloperAPISystemStatus()
        ss = s.set_status("inst-1", [{"name": "API", "status": "degraded"}])
        assert ss.overall == "partial_degradation"

    def test_default(self):
        s = AppAPIDeveloperAPISystemStatus()
        assert s.get("inst-1").overall == "all_systems_operational"
