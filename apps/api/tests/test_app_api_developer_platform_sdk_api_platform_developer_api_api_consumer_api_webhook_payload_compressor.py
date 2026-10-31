import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_payload_compressor import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressor

class TestPayloadCompressor:
    def test_compress(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressor()
        payload = '{"event":"test","data":' + '"x" ' * 500 + '}'
        result = svc.compress("inst-1", payload)
        assert result.compressed_size < result.original_size
        assert result.compression_ratio > 0

    def test_savings(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressor()
        svc.compress("inst-1", "a" * 1000)
        savings = svc.savings("inst-1")
        assert savings["saved_bytes"] > 0 and savings["savings_pct"] > 0

    def test_invalid_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressor()
        with pytest.raises(ValueError, match="Invalid algorithm"):
            svc.compress("inst-1", "test", "brotli")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadCompressor()
        svc.compress("inst-1", "test data")
        assert svc.savings("inst-2")["payloads_compressed"] == 0
