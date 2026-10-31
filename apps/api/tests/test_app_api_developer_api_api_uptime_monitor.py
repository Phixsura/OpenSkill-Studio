from app.services.app_api_developer_api_api_uptime_monitor import AppAPIDeveloperAPIApiUptimeMonitor

class TestUptimeMonitor:
    def test_all_up(self):
        m = AppAPIDeveloperAPIApiUptimeMonitor()
        m.record_window("inst-1", "/api", 3600, "up")
        assert m.get_uptime("inst-1", "/api") == 100.0

    def test_partial_down(self):
        m = AppAPIDeveloperAPIApiUptimeMonitor()
        m.record_window("inst-1", "/api", 900, "up")
        m.record_window("inst-1", "/api", 100, "down")
        r = m.all_records("inst-1")[0]
        assert r.uptime_pct < 100.0
        assert r.total_downtime_minutes > 0

    def test_below_threshold(self):
        m = AppAPIDeveloperAPIApiUptimeMonitor()
        m.record_window("inst-1", "/a", 3600, "up")
        m.record_window("inst-1", "/b", 100, "up")
        m.record_window("inst-1", "/b", 100, "down")
        assert len(m.below_threshold("inst-1", 99.9)) == 1

    def test_default_uptime(self):
        m = AppAPIDeveloperAPIApiUptimeMonitor()
        assert m.get_uptime("inst-1", "/unknown") == 100.0

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiUptimeMonitor()
        m.record_window("inst-1", "/api", 3600, "up")
        assert len(m.all_records("inst-2")) == 0
