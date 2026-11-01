from app.services.app_api_developer_api_api_response_time_percentiles import AppAPIDeveloperAPIApiResponseTimePercentiles

class TestResponseTimePercentiles:
    def test_record_and_calculate(self):
        p = AppAPIDeveloperAPIApiResponseTimePercentiles()
        for i in range(100): p.record("inst-1", "/api/users", float(i + 1))
        r = p.calculate("inst-1", "/api/users")
        assert r.p50 == 51.0
        assert r.p99 == 100.0
        assert r.count == 100

    def test_empty(self):
        p = AppAPIDeveloperAPIApiResponseTimePercentiles()
        r = p.calculate("inst-1", "/api/users")
        assert r.count == 0

    def test_slowest(self):
        p = AppAPIDeveloperAPIApiResponseTimePercentiles()
        for i in range(10): p.record("inst-1", "/fast", 10.0)
        for i in range(10): p.record("inst-1", "/slow", 500.0)
        slowest = p.slowest_p99("inst-1", 1)
        assert slowest[0].endpoint == "/slow"

    def test_isolation(self):
        p = AppAPIDeveloperAPIApiResponseTimePercentiles()
        p.record("inst-1", "/api", 50.0)
        assert len(p.all_endpoints("inst-2")) == 0
