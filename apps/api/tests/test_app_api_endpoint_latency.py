from app.services.app_api_endpoint_latency import AppAPIEndpointLatency

class TestLatency:
    def test_record(self):
        l = AppAPIEndpointLatency()
        el = l.record("inst-1", "GET", "/api/users", 50.0)
        assert el.avg == 50.0

    def test_avg(self):
        l = AppAPIEndpointLatency()
        l.record("inst-1", "GET", "/api", 100)
        l.record("inst-1", "GET", "/api", 200)
        assert l.list_endpoints("inst-1")[0].avg == 150.0

    def test_slowest(self):
        l = AppAPIEndpointLatency()
        l.record("inst-1", "GET", "/fast", 10)
        l.record("inst-1", "GET", "/slow", 500)
        assert l.slowest("inst-1")[0].path == "/slow"

    def test_isolation(self):
        l = AppAPIEndpointLatency()
        l.record("inst-1", "GET", "/api", 50)
        assert l.list_endpoints("inst-2") == []
