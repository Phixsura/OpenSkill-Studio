from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_api_consumer_lifetime_value import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue

class TestConsumerLTV:
    def test_ltv(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue()
        c = l.update("inst-1", "c1", 120000, 12, 10000, "pro")
        assert c.ltv_cents == 240000  # $100/mo * 24
        assert c.arpu_cents == 10000

    def test_top_ltv(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue()
        l.update("inst-1", "c1", 10000, 10, 1000, "starter")
        l.update("inst-1", "c2", 100000, 10, 10000, "enterprise")
        top = l.top_ltv("inst-1", 1)
        assert top[0].consumer_id == "c2"

    def test_at_risk(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue()
        l.update("inst-1", "c1", 50000, 6, 8000, "pro", "high")
        l.update("inst-1", "c2", 50000, 6, 8000, "pro", "low")
        assert len(l.at_risk("inst-1")) == 1

    def test_total_mrr(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue()
        l.update("inst-1", "c1", 10000, 5, 2000, "starter")
        l.update("inst-1", "c2", 50000, 10, 5000, "pro")
        assert l.total_mrr_cents("inst-1") == 7000

    def test_isolation(self):
        l = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiConsumerLifetimeValue()
        l.update("inst-1", "c1", 10000, 5, 2000, "starter")
        assert l.total_mrr_cents("inst-2") == 0
