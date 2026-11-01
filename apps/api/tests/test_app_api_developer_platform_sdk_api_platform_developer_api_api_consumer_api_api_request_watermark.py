from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_watermark import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark

class TestRequestWatermark:
    def test_generate_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark()
        wm = svc.generate("inst-1", "c1", "req-123")
        assert len(wm.watermark_id) == 20
        verified = svc.verify("inst-1", wm.watermark_id)
        assert verified is not None and verified.consumer_id == "c1"

    def test_trace(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark()
        wm = svc.generate("inst-1", "c1", "req-456")
        trace = svc.trace("inst-1", wm.watermark_id)
        assert trace["consumer_id"] == "c1" and trace["request_id"] == "req-456"

    def test_unknown_watermark(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark()
        assert svc.verify("inst-1", "nonexistent") is None

    def test_unique_watermarks(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark()
        wm1 = svc.generate("inst-1", "c1", "req-1")
        wm2 = svc.generate("inst-1", "c1", "req-1")
        assert wm1.watermark_id != wm2.watermark_id

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestWatermark()
        svc.generate("inst-1", "c1", "req-1")
        assert svc.watermark_count("inst-2") == 0
