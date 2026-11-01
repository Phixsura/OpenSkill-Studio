from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_usage_sparkline import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparkline

class TestUsageSparkline:
    def test_add_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparkline()
        for i in range(12): svc.add_point("inst-1", "c1", "requests", f"h{i}", 100 + i * 10)
        spark = svc.get_sparkline("inst-1", "c1", "requests")
        assert len(spark.points) == 12
        assert spark.trend == "up"  # increasing

    def test_stable_trend(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparkline()
        for i in range(12): svc.add_point("inst-1", "c1", "requests", f"h{i}", 100)
        assert svc.get_sparkline("inst-1", "c1", "requests").trend == "stable"

    def test_down_trend(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparkline()
        for i in range(12): svc.add_point("inst-1", "c1", "errors", f"h{i}", 200 - i * 15)
        assert svc.get_sparkline("inst-1", "c1", "errors").trend == "down"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUsageSparkline()
        svc.add_point("inst-1", "c1", "requests", "h1", 100)
        assert svc.consumer_count("inst-2") == 0
