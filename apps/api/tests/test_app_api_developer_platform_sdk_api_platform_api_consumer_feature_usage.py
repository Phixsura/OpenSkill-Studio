from app.services.app_api_developer_platform_sdk_api_platform_api_consumer_feature_usage import AppAPIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsage

class TestConsumerFeatureUsage:
    def test_track(self):
        u = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsage()
        c = u.track("inst-1", "c1", "webhooks", 10)
        assert c.feature_count == 1
        assert c.top_feature == "webhooks"

    def test_popularity(self):
        u = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsage()
        u.track("inst-1", "c1", "webhooks")
        u.track("inst-1", "c2", "webhooks")
        u.track("inst-1", "c3", "graphql")
        pop = u.feature_popularity("inst-1")
        assert pop["webhooks"] == 2

    def test_low_adoption(self):
        u = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsage()
        for i in range(10): u.track("inst-1", f"c{i}", "webhooks")
        u.track("inst-1", "c1", "graphql")
        assert "graphql" in u.low_adoption_features("inst-1", 5)

    def test_isolation(self):
        u = AppAPIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsage()
        u.track("inst-1", "c1", "webhooks")
        assert len(u.all_usage("inst-2")) == 0
