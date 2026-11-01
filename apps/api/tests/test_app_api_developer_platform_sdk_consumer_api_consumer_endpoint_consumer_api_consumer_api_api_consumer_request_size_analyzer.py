import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_api_consumer_request_size_analyzer import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer, SizeRecord,
)

class TestRequestSizeAnalyzer:
    def test_record_and_analyze(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer()
        svc.record("inst-1", SizeRecord(endpoint_path="/api/users", method="GET", request_bytes=100, response_bytes=5000))
        svc.record("inst-1", SizeRecord(endpoint_path="/api/users", method="GET", request_bytes=120, response_bytes=8000))
        analysis = svc.analyze_endpoint("inst-1", "/api/users")
        assert analysis.sample_count == 2 and analysis.max_response_bytes == 8000

    def test_avg_calculation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer()
        svc.record("inst-1", SizeRecord(endpoint_path="/api", method="POST", request_bytes=1000, response_bytes=2000))
        svc.record("inst-1", SizeRecord(endpoint_path="/api", method="POST", request_bytes=3000, response_bytes=4000))
        analysis = svc.analyze_endpoint("inst-1", "/api")
        assert analysis.avg_request_bytes == 2000 and analysis.avg_response_bytes == 3000

    def test_platform_stats(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer()
        svc.record("inst-1", SizeRecord(endpoint_path="/api/users", method="GET", request_bytes=100, response_bytes=5000))
        svc.record("inst-1", SizeRecord(endpoint_path="/api/orders", method="GET", request_bytes=200, response_bytes=10000))
        stats = svc.get_platform_stats("inst-1")
        assert stats.total_endpoints == 2 and stats.largest_endpoint == "/api/orders"

    def test_negative_rejected(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer()
        with pytest.raises(ValueError, match="non-negative"):
            svc.record("inst-1", SizeRecord(endpoint_path="/api", method="GET", request_bytes=-1, response_bytes=0))

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer()
        assert svc.analyze_endpoint("inst-1", "/missing").sample_count == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiApiConsumerRequestSizeAnalyzer()
        svc.record("inst-1", SizeRecord(endpoint_path="/api", method="GET", request_bytes=100, response_bytes=1000))
        assert len(svc.list_endpoints("inst-2")) == 0
