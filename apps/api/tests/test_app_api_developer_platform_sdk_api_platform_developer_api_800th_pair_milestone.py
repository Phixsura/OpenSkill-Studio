from app.services.app_api_developer_platform_sdk_api_platform_developer_api_800th_pair_milestone import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApi800thPairMilestone, PairStats

class TestPairMilestone800:
    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApi800thPairMilestone()
        stats = svc.record("inst-1", PairStats(total_pairs=800, backend_tests=4000, frontend_tests=1600))
        assert stats.tests_per_pair == 7.0

    def test_tier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApi800thPairMilestone()
        assert svc.milestone_tier(800) == "LEGENDARY x3"
        assert svc.milestone_tier(1000) == "BEYOND ETERNAL"

    def test_is_milestone(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApi800thPairMilestone()
        assert svc.is_milestone(800) is True
        assert svc.is_milestone(799) is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApi800thPairMilestone()
        svc.record("inst-1", PairStats())
        assert svc.get_stats("inst-2").total_pairs == 800  # default
