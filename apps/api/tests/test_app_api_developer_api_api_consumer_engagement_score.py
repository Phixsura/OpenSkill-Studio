from app.services.app_api_developer_api_api_consumer_engagement_score import AppAPIDeveloperAPIApiConsumerEngagementScore

class TestEngagementScore:
    def test_champion(self):
        e = AppAPIDeveloperAPIApiConsumerEngagementScore()
        s = e.calculate("inst-1", "c1", 200, 15, 0.5, 0, True, True)
        assert s.tier == "champion"
        assert s.score >= 80

    def test_dormant(self):
        e = AppAPIDeveloperAPIApiConsumerEngagementScore()
        s = e.calculate("inst-1", "c1", 0, 0, 50, 90)
        assert s.tier == "dormant"

    def test_ranked(self):
        e = AppAPIDeveloperAPIApiConsumerEngagementScore()
        e.calculate("inst-1", "c1", 200, 15, 0.5, 0, True, True)
        e.calculate("inst-1", "c2", 1, 1, 10, 30)
        ranked = e.ranked("inst-1")
        assert ranked[0].consumer_id == "c1"

    def test_by_tier(self):
        e = AppAPIDeveloperAPIApiConsumerEngagementScore()
        e.calculate("inst-1", "c1", 200, 15, 0.5, 0, True, True)
        e.calculate("inst-1", "c2", 0, 0, 50, 90)
        tiers = e.by_tier("inst-1")
        assert "champion" in tiers
        assert "dormant" in tiers

    def test_isolation(self):
        e = AppAPIDeveloperAPIApiConsumerEngagementScore()
        e.calculate("inst-1", "c1", 100, 10, 1, 0)
        assert len(e.ranked("inst-2")) == 0
