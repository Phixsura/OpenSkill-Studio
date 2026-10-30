from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_request_correlation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelation, CorrelatedRequest,
)

class TestRequestCorrelation:
    def test_record_and_get_trace(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelation()
        tid = svc.generate_trace_id()
        svc.record("inst-1", CorrelatedRequest(request_id="r1", trace_id=tid, span_id="s1", method="GET", path="/users", status_code=200, duration_ms=50))
        svc.record("inst-1", CorrelatedRequest(request_id="r2", trace_id=tid, span_id="s2", parent_span_id="s1", method="GET", path="/db", status_code=200, duration_ms=20))
        trace = svc.get_trace("inst-1", tid)
        assert len(trace) == 2

    def test_trace_duration(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(request_id="r1", trace_id="t1", span_id="s1", duration_ms=100))
        svc.record("inst-1", CorrelatedRequest(request_id="r2", trace_id="t1", span_id="s2", duration_ms=50))
        assert svc.trace_duration("inst-1", "t1") == 150.0

    def test_failed_traces(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(request_id="r1", trace_id="t1", span_id="s1", status_code=200))
        svc.record("inst-1", CorrelatedRequest(request_id="r2", trace_id="t2", span_id="s2", status_code=500))
        assert "t2" in svc.failed_traces("inst-1")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestCorrelation()
        svc.record("inst-1", CorrelatedRequest(request_id="r1", trace_id="t1", span_id="s1"))
        assert svc.trace_count("inst-2") == 0
