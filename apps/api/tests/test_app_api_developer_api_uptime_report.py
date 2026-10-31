from app.services.app_api_developer_api_uptime_report import AppAPIDeveloperAPIUptimeReport

class TestUptimeReport:
    def test_generate(self):
        u = AppAPIDeveloperAPIUptimeReport()
        r = u.generate("inst-1", "r1", "2024-01", 99.95, 43200, 21.6, 1)
        assert r.uptime_pct == 99.95

    def test_best(self):
        u = AppAPIDeveloperAPIUptimeReport()
        u.generate("inst-1", "r1", "2024-01", 99.9, 43200, 43.2, 2)
        u.generate("inst-1", "r2", "2024-02", 99.99, 40320, 4.0, 0)
        assert u.best_period("inst-1").period == "2024-02"

    def test_isolation(self):
        u = AppAPIDeveloperAPIUptimeReport()
        u.generate("inst-1", "r1", "2024-01", 99.9, 1000, 10, 0)
        assert u.list_reports("inst-2") == []
