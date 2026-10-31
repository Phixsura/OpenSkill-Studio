from app.services.app_api_developer_api_api_developer_api_api_consumer_usage_trend import AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend

class TestConsumerUsageTrend:
    def test_add_daily(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend()
        for v in [100, 200, 300]: t.add_daily("inst-1", "c1", v)
        assert t.get("inst-1", "c1").total == 600

    def test_growing(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend()
        for v in [100, 110, 120, 200, 250, 300]: t.add_daily("inst-1", "c1", v)
        assert t.get("inst-1", "c1").trend == "growing"

    def test_declining(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend()
        for v in [300, 280, 260, 100, 80, 60]: t.add_daily("inst-1", "c1", v)
        assert t.get("inst-1", "c1").trend == "declining"

    def test_top(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend()
        for v in [100]: t.add_daily("inst-1", "c1", v)
        for v in [1000]: t.add_daily("inst-1", "c2", v)
        assert t.top_consumers("inst-1", 1)[0].consumer_id == "c2"

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiConsumerUsageTrend()
        t.add_daily("inst-1", "c1", 100)
        assert len(t.top_consumers("inst-2")) == 0
