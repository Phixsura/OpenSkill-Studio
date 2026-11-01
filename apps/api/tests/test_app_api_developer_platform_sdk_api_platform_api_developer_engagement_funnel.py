from app.services.app_api_developer_platform_sdk_api_platform_api_developer_engagement_funnel import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnel

class TestEngagementFunnel:
    def test_update(self):
        f = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnel()
        ef = f.update("inst-1", {"visited_docs": 1000, "created_account": 500, "generated_key": 400, "first_call": 300, "regular_usage": 150, "power_user": 50})
        assert ef.conversion_rate == 5.0

    def test_biggest_dropoff(self):
        f = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnel()
        ef = f.update("inst-1", {"visited_docs": 1000, "created_account": 200, "generated_key": 190, "first_call": 180, "regular_usage": 170, "power_user": 160})
        assert ef.biggest_dropoff == "created_account"

    def test_empty(self):
        f = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnel()
        assert f.get("inst-1") is None

    def test_isolation(self):
        f = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperEngagementFunnel()
        f.update("inst-1", {"visited_docs": 100})
        assert f.get("inst-2") is None
