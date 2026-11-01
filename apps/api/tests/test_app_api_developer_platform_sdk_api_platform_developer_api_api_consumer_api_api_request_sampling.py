from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_sampling import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling, SampledRequest,
)

class TestRequestSampling:
    def test_deterministic_sampling(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling(sample_rate=1.0)
        assert svc.should_sample("any-request") is True

    def test_record_and_recent(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling()
        svc.record("inst-1", SampledRequest(sample_id="s1", method="GET", path="/users", status_code=200, duration_ms=50, consumer_id="c1"))
        recent = svc.recent("inst-1")
        assert len(recent) == 1

    def test_filter_by_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling()
        svc.record("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200, duration_ms=10, consumer_id="c1"))
        svc.record("inst-1", SampledRequest(sample_id="s2", method="GET", path="/b", status_code=500, duration_ms=100, consumer_id="c1"))
        errors = svc.recent("inst-1", status_min=500)
        assert len(errors) == 1

    def test_avg_duration(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling()
        svc.record("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200, duration_ms=40, consumer_id="c1"))
        svc.record("inst-1", SampledRequest(sample_id="s2", method="GET", path="/a", status_code=200, duration_ms=60, consumer_id="c1"))
        assert svc.avg_duration("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestSampling()
        svc.record("inst-1", SampledRequest(sample_id="s1", method="GET", path="/a", status_code=200, duration_ms=10, consumer_id="c1"))
        assert svc.sample_count("inst-2") == 0
