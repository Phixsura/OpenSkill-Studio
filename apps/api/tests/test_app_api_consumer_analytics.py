from app.services.app_api_consumer_analytics import AppAPIConsumerAnalytics

class TestAnalytics:
    def test_record(self):
        a = AppAPIConsumerAnalytics()
        ca = a.record("inst-1", "c1", "/api/users", 50.0, True)
        assert ca.total_requests == 1

    def test_error_rate(self):
        a = AppAPIConsumerAnalytics()
        for _ in range(8): a.record("inst-1", "c1", "/api", 50, True)
        for _ in range(2): a.record("inst-1", "c1", "/api", 50, False)
        assert a.get("inst-1", "c1").error_rate == 20.0

    def test_top_consumers(self):
        a = AppAPIConsumerAnalytics()
        for _ in range(10): a.record("inst-1", "c1", "/api", 50, True)
        for _ in range(5): a.record("inst-1", "c2", "/api", 50, True)
        top = a.top_consumers("inst-1")
        assert top[0].consumer_id == "c1"

    def test_isolation(self):
        a = AppAPIConsumerAnalytics()
        a.record("inst-1", "c1", "/api", 50, True)
        assert a.top_consumers("inst-2") == []
