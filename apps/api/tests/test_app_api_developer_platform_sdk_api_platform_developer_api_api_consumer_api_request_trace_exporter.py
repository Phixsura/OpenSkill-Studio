import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_request_trace_exporter import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter, TraceSpan,
)

class TestRequestTraceExporter:
    def test_record_and_export(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter()
        svc.record_span("inst-1", TraceSpan(span_id="s1", trace_id="t1", operation="GET /users", service="api", duration_ms=50))
        export = svc.export_traces("inst-1", "e1", "otlp")
        assert export.span_count == 1

    def test_error_spans(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter()
        svc.record_span("inst-1", TraceSpan(span_id="s1", trace_id="t1", operation="GET /a", service="api", duration_ms=10))
        svc.record_span("inst-1", TraceSpan(span_id="s2", trace_id="t1", operation="DB query", service="db", duration_ms=100, status="error"))
        assert len(svc.error_spans("inst-1")) == 1

    def test_invalid_format(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter()
        with pytest.raises(ValueError, match="Invalid format"):
            svc.export_traces("inst-1", "e1", "invalid")

    def test_trace_ids(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter()
        svc.record_span("inst-1", TraceSpan(span_id="s1", trace_id="t1", operation="x", service="a", duration_ms=10))
        svc.record_span("inst-1", TraceSpan(span_id="s2", trace_id="t2", operation="y", service="a", duration_ms=10))
        assert len(svc.trace_ids("inst-1")) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter()
        svc.record_span("inst-1", TraceSpan(span_id="s1", trace_id="t1", operation="x", service="a", duration_ms=10))
        assert svc.span_count("inst-2") == 0
