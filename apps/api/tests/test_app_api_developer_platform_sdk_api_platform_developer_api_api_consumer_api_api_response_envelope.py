from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_response_envelope import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope, EnvelopeConfig,
)

class TestResponseEnvelope:
    def test_default_wrap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope()
        result = svc.wrap("inst-1", "c1", [{"id": 1}])
        assert result["data"] == [{"id": 1}]

    def test_custom_wrap_key(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope()
        svc.configure("inst-1", EnvelopeConfig(consumer_id="c1", wrap_key="results"))
        result = svc.wrap("inst-1", "c1", [1, 2, 3])
        assert "results" in result

    def test_meta_with_pagination(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope()
        svc.configure("inst-1", EnvelopeConfig(consumer_id="c1"))
        result = svc.wrap("inst-1", "c1", [], request_id="req-123", total=50, page=1)
        assert result["meta"]["total"] == 50
        assert result["meta"]["request_id"] == "req-123"

    def test_no_meta(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope()
        svc.configure("inst-1", EnvelopeConfig(consumer_id="c1", include_meta=False))
        result = svc.wrap("inst-1", "c1", {"x": 1})
        assert "meta" not in result

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope()
        svc.configure("inst-1", EnvelopeConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
