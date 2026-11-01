import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_response_compression import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression, CompressionConfig,
)

class TestEndpointResponseCompression:
    def test_should_compress(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression()
        svc.configure("inst-1", CompressionConfig(endpoint_path="/api", algorithm="gzip", min_size_bytes=100))
        assert svc.should_compress("inst-1", "/api", "application/json", 500)
        assert not svc.should_compress("inst-1", "/api", "application/json", 50)

    def test_content_type_filter(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression()
        svc.configure("inst-1", CompressionConfig(endpoint_path="/api", content_types=["application/json"]))
        assert svc.should_compress("inst-1", "/api", "application/json; charset=utf-8", 5000)
        assert not svc.should_compress("inst-1", "/api", "image/png", 5000)

    def test_none_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression()
        svc.configure("inst-1", CompressionConfig(endpoint_path="/api", algorithm="none"))
        assert not svc.should_compress("inst-1", "/api", "application/json", 5000)

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression()
        svc.record_compression("inst-1", "/api", 1000, 300)
        svc.record_compression("inst-1", "/api", 2000, 600)
        stats = svc.get_stats("inst-1", "/api")
        assert stats.compressed_count == 2 and stats.savings_pct == 70.0

    def test_invalid_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression()
        with pytest.raises(ValueError, match="Invalid algorithm"):
            svc.configure("inst-1", CompressionConfig(endpoint_path="/api", algorithm="lz4"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointResponseCompression()
        svc.configure("inst-1", CompressionConfig(endpoint_path="/api"))
        assert len(svc.list_configs("inst-2")) == 0
