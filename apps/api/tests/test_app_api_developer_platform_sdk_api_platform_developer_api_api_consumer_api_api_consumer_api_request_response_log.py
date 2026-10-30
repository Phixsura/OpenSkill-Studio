from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_response_log import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog, RequestResponsePair,
)

class TestRequestResponseLog:
    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog()
        svc.record("inst-1", RequestResponsePair(pair_id="p1", method="GET", path="/users", request_status=200, duration_ms=50, consumer_id="c1"))
        entries = svc.query("inst-1", consumer_id="c1")
        assert len(entries) == 1

    def test_filter_by_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog()
        svc.record("inst-1", RequestResponsePair(pair_id="p1", method="GET", path="/a", request_status=200, duration_ms=10))
        svc.record("inst-1", RequestResponsePair(pair_id="p2", method="GET", path="/b", request_status=500, duration_ms=100))
        errors = svc.query("inst-1", status_min=500)
        assert len(errors) == 1

    def test_avg_duration(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog()
        svc.record("inst-1", RequestResponsePair(pair_id="p1", method="GET", path="/a", request_status=200, duration_ms=40))
        svc.record("inst-1", RequestResponsePair(pair_id="p2", method="GET", path="/a", request_status=200, duration_ms=60))
        assert svc.avg_duration("inst-1") == 50.0

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog(max_entries=500)
        for i in range(700): svc.record("inst-1", RequestResponsePair(pair_id=f"p{i}", method="GET", path="/a", request_status=200, duration_ms=10))
        assert svc.entry_count("inst-1") == 500

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestResponseLog()
        svc.record("inst-1", RequestResponsePair(pair_id="p1", method="GET", path="/a", request_status=200, duration_ms=10))
        assert svc.entry_count("inst-2") == 0
