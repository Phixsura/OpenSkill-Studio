from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_api_endpoint_throughput_monitor import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor

class TestThroughputMonitor:
    def test_record(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor()
        s = m.record("inst-1", "/api/users", 500.0)
        assert s.rps == 500.0

    def test_peak(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor()
        m.record("inst-1", "/api", 100)
        m.record("inst-1", "/api", 500)
        m.record("inst-1", "/api", 200)
        s = m.all_endpoints("inst-1")[0]
        assert s.peak_rps == 500

    def test_avg(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor()
        m.record("inst-1", "/api", 100)
        m.record("inst-1", "/api", 300)
        assert m.all_endpoints("inst-1")[0].avg_rps == 200.0

    def test_hottest(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor()
        m.record("inst-1", "/slow", 10)
        m.record("inst-1", "/fast", 1000)
        assert m.hottest("inst-1", 1)[0].endpoint == "/fast"

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitor()
        m.record("inst-1", "/api", 100)
        assert len(m.all_endpoints("inst-2")) == 0
