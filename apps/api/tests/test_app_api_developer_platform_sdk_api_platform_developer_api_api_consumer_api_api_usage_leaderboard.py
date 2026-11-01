from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_usage_leaderboard import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboard

class TestUsageLeaderboard:
    def test_ranking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboard()
        svc.record_usage("inst-1", "c1", 1000, 990, 50000)
        svc.record_usage("inst-1", "c2", 5000, 4900, 200000)
        lb = svc.leaderboard("inst-1")
        assert lb[0].consumer_id == "c2"  # more requests, higher score
        assert lb[0].rank == 1

    def test_consumer_rank(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboard()
        svc.record_usage("inst-1", "c1", 100, 95, 5000)
        svc.record_usage("inst-1", "c2", 500, 490, 20000)
        assert svc.consumer_rank("inst-1", "c1") == 2

    def test_unknown_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboard()
        assert svc.consumer_rank("inst-1", "nobody") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboard()
        svc.record_usage("inst-1", "c1", 100, 90, 5000)
        assert svc.consumer_count("inst-2") == 0
