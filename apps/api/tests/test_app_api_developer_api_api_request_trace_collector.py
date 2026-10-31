from app.services.app_api_developer_api_api_request_trace_collector import AppAPIDeveloperAPIApiRequestTraceCollector

class TestTraceCollector:
    def test_record_span(self):
        c = AppAPIDeveloperAPIApiRequestTraceCollector()
        t = c.record_span("inst-1", "t1", "s1", "GET /api/users", "api-gateway", 50)
        assert len(t.spans) == 1

    def test_multi_span_trace(self):
        c = AppAPIDeveloperAPIApiRequestTraceCollector()
        c.record_span("inst-1", "t1", "s1", "GET /api", "gateway", 100)
        c.record_span("inst-1", "t1", "s2", "query users", "db", 50, parent_span_id="s1")
        t = c.get_trace("inst-1", "t1")
        assert len(t.spans) == 2

    def test_error_traces(self):
        c = AppAPIDeveloperAPIApiRequestTraceCollector()
        c.record_span("inst-1", "t1", "s1", "GET /api", "gateway", 50)
        c.record_span("inst-1", "t2", "s2", "POST /api", "gateway", 100, status="error")
        assert len(c.error_traces("inst-1")) == 1

    def test_has_errors(self):
        c = AppAPIDeveloperAPIApiRequestTraceCollector()
        c.record_span("inst-1", "t1", "s1", "op", "svc", 50, status="error")
        assert c.get_trace("inst-1", "t1").has_errors is True

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiRequestTraceCollector()
        c.record_span("inst-1", "t1", "s1", "op", "svc", 50)
        assert c.trace_count("inst-2") == 0
