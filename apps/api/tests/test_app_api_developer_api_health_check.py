from app.services.app_api_developer_api_health_check import AppAPIDeveloperAPIHealthCheck

class TestHealthCheck:
    def test_run(self):
        h = AppAPIDeveloperAPIHealthCheck()
        r = h.run_check("inst-1", "database", "pass", "Connected", 5.0)
        assert r.status == "pass"

    def test_all_passing(self):
        h = AppAPIDeveloperAPIHealthCheck()
        h.run_check("inst-1", "db", "pass")
        h.run_check("inst-1", "cache", "pass")
        assert h.all_passing("inst-1") is True

    def test_failing(self):
        h = AppAPIDeveloperAPIHealthCheck()
        h.run_check("inst-1", "db", "pass")
        h.run_check("inst-1", "cache", "fail", "Connection refused")
        assert h.all_passing("inst-1") is False

    def test_isolation(self):
        h = AppAPIDeveloperAPIHealthCheck()
        h.run_check("inst-1", "db", "fail")
        assert h.all_passing("inst-2") is True
