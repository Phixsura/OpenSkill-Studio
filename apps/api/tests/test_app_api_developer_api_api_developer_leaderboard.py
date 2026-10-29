from app.services.app_api_developer_api_api_developer_leaderboard import AppAPIDeveloperAPIApiDeveloperLeaderboard

class TestDeveloperLeaderboard:
    def test_update(self):
        lb = AppAPIDeveloperAPIApiDeveloperLeaderboard()
        e = lb.update("inst-1", "d1", "Alice", api_calls=50000, apps_created=5)
        assert e.total_score == 750  # 500 + 250

    def test_top(self):
        lb = AppAPIDeveloperAPIApiDeveloperLeaderboard()
        lb.update("inst-1", "d1", "Alice", api_calls=10000)
        lb.update("inst-1", "d2", "Bob", api_calls=50000)
        top = lb.top("inst-1", 1)
        assert top[0].developer_id == "d2"

    def test_rank_tier(self):
        lb = AppAPIDeveloperAPIApiDeveloperLeaderboard()
        e = lb.update("inst-1", "d1", "Alice", api_calls=100000, apps_created=10)
        assert e.rank_tier == "diamond"

    def test_tier_counts(self):
        lb = AppAPIDeveloperAPIApiDeveloperLeaderboard()
        lb.update("inst-1", "d1", "A", api_calls=100000, apps_created=10)
        lb.update("inst-1", "d2", "B", api_calls=100)
        tiers = lb.tier_counts("inst-1")
        assert "diamond" in tiers
        assert "bronze" in tiers

    def test_isolation(self):
        lb = AppAPIDeveloperAPIApiDeveloperLeaderboard()
        lb.update("inst-1", "d1", "A", api_calls=1000)
        assert len(lb.top("inst-2")) == 0
