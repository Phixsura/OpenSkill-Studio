import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_endpoint_consumer_api_consumer_api_endpoint_geographic_analytics import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics, GeoRecord,
)

class TestGeographicAnalytics:
    def test_record_and_analyze(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics()
        svc.record("inst-1", "c1", GeoRecord(country_code="US", region="NA", request_count=5000, avg_latency_ms=50, error_count=10))
        svc.record("inst-1", "c1", GeoRecord(country_code="DE", region="EU", request_count=2000, avg_latency_ms=120, error_count=5))
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.total_requests == 7000 and analytics.unique_countries == 2

    def test_by_region(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics()
        svc.record("inst-1", "c1", GeoRecord(country_code="US", region="NA", request_count=100))
        svc.record("inst-1", "c1", GeoRecord(country_code="CA", region="NA", request_count=50))
        svc.record("inst-1", "c1", GeoRecord(country_code="DE", region="EU", request_count=80))
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.by_region["NA"] == 150

    def test_highest_latency(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics()
        svc.record("inst-1", "c1", GeoRecord(country_code="US", region="NA", request_count=100, avg_latency_ms=50))
        svc.record("inst-1", "c1", GeoRecord(country_code="AU", region="APAC", request_count=50, avg_latency_ms=300))
        assert svc.analyze("inst-1", "c1").highest_latency_country == "AU"

    def test_merge_same_country(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics()
        svc.record("inst-1", "c1", GeoRecord(country_code="US", region="NA", request_count=100, error_count=5))
        svc.record("inst-1", "c1", GeoRecord(country_code="US", region="NA", request_count=200, error_count=10))
        analytics = svc.analyze("inst-1", "c1")
        assert analytics.unique_countries == 1 and analytics.total_requests == 300

    def test_invalid_region(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics()
        with pytest.raises(ValueError, match="Invalid region"):
            svc.record("inst-1", "c1", GeoRecord(country_code="XX", region="INVALID"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiEndpointConsumerApiConsumerApiEndpointGeographicAnalytics()
        svc.record("inst-1", "c1", GeoRecord(country_code="US", region="NA", request_count=100))
        assert svc.analyze("inst-2", "c1").total_requests == 0
