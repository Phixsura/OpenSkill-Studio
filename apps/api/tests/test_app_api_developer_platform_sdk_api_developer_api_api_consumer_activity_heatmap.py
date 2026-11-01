from app.services.app_api_developer_platform_sdk_api_developer_api_api_consumer_activity_heatmap import AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmap

class TestConsumerActivityHeatmap:
    def test_record(self):
        h = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmap()
        m = h.record("inst-1", "c1", 0, 9, 100)
        assert m.total_activity == 100

    def test_peak_hour(self):
        h = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmap()
        h.record("inst-1", "c1", 0, 9, 100)
        h.record("inst-1", "c1", 0, 14, 500)
        h.record("inst-1", "c1", 1, 9, 50)
        assert h.get("inst-1", "c1").peak_hour == 14

    def test_most_active(self):
        h = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmap()
        h.record("inst-1", "c1", 0, 9, 100)
        h.record("inst-1", "c2", 0, 9, 500)
        top = h.most_active("inst-1", 1)
        assert top[0].consumer_id == "c2"

    def test_isolation(self):
        h = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerActivityHeatmap()
        h.record("inst-1", "c1", 0, 9)
        assert len(h.all_maps("inst-2")) == 0
