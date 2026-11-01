from app.services.app_api_developer_api_api_developer_api_api_consumer_api_usage_breakdown import AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown

class TestConsumerUsageBreakdown:
    def test_record(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown()
        r = b.record("inst-1", "c1", "/api/users", "GET", 100)
        assert r.total_calls == 100

    def test_accumulate(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown()
        b.record("inst-1", "c1", "/api/users", "GET", 100)
        b.record("inst-1", "c1", "/api/users", "GET", 50)
        assert b.get("inst-1", "c1").total_calls == 150

    def test_multiple_endpoints(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown()
        b.record("inst-1", "c1", "/api/users", "GET", 100)
        b.record("inst-1", "c1", "/api/orders", "POST", 50)
        assert b.get("inst-1", "c1").unique_endpoints == 2

    def test_top_consumers(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown()
        b.record("inst-1", "c1", "/api", "GET", 100)
        b.record("inst-1", "c2", "/api", "GET", 500)
        top = b.top_consumers("inst-1", 1)
        assert top[0].consumer_id == "c2"

    def test_isolation(self):
        b = AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown()
        b.record("inst-1", "c1", "/api", "GET", 100)
        assert len(b.top_consumers("inst-2")) == 0
