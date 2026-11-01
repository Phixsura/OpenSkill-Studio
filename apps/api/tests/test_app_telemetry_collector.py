"""Tests for App Telemetry Collector — metrics, errors, spans, quotas, summary."""

import pytest

from app.services.app_telemetry_collector import (
    AppTelemetryCollector,
    ErrorReport,
    MetricKind,
    PerformanceSpan,
    TELEMETRY_QUOTA_PER_HOUR,
    TelemetryMetric,
)


class TestMetrics:
    def test_record_metric(self):
        c = AppTelemetryCollector()
        m = TelemetryMetric("request_count", MetricKind.COUNTER, 1)
        assert c.record_metric("inst-1", m) is True
        assert len(c.get_metrics("inst-1")) == 1

    def test_filter_by_name(self):
        c = AppTelemetryCollector()
        c.record_metric("inst-1", TelemetryMetric("a", MetricKind.COUNTER, 1))
        c.record_metric("inst-1", TelemetryMetric("b", MetricKind.GAUGE, 42))
        assert len(c.get_metrics("inst-1", name="a")) == 1

    def test_metric_tags(self):
        c = AppTelemetryCollector()
        m = TelemetryMetric("latency", MetricKind.HISTOGRAM, 150, tags={"endpoint": "/api"})
        c.record_metric("inst-1", m)
        assert c.get_metrics("inst-1")[0].tags["endpoint"] == "/api"


class TestErrors:
    def test_report_error(self):
        c = AppTelemetryCollector()
        err = ErrorReport("ValueError", "invalid input", stack_trace="line 5...")
        assert c.report_error("inst-1", err) is True
        errors = c.get_errors("inst-1")
        assert len(errors) == 1
        assert errors[0].error_type == "ValueError"

    def test_error_context(self):
        c = AppTelemetryCollector()
        err = ErrorReport("TimeoutError", "timed out", context={"url": "https://api.example.com"})
        c.report_error("inst-1", err)
        assert c.get_errors("inst-1")[0].context["url"] == "https://api.example.com"

    def test_multiple_errors(self):
        c = AppTelemetryCollector()
        for i in range(5):
            c.report_error("inst-1", ErrorReport("Error", f"msg-{i}"))
        assert len(c.get_errors("inst-1")) == 5


class TestSpans:
    def test_record_span(self):
        c = AppTelemetryCollector()
        span = PerformanceSpan("db_query", 45.2, status="ok")
        assert c.record_span("inst-1", span) is True
        spans = c.get_spans("inst-1")
        assert len(spans) == 1
        assert spans[0].duration_ms == 45.2

    def test_filter_by_operation(self):
        c = AppTelemetryCollector()
        c.record_span("inst-1", PerformanceSpan("db_query", 10))
        c.record_span("inst-1", PerformanceSpan("api_call", 200))
        assert len(c.get_spans("inst-1", operation="db_query")) == 1

    def test_span_tags(self):
        c = AppTelemetryCollector()
        c.record_span("inst-1", PerformanceSpan("render", 30, tags={"component": "header"}))
        assert c.get_spans("inst-1")[0].tags["component"] == "header"


class TestQuota:
    def test_within_quota(self):
        c = AppTelemetryCollector()
        for i in range(10):
            assert c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1)) is True
        assert c.get_quota_usage("inst-1") == 10

    def test_quota_exceeded(self):
        c = AppTelemetryCollector()
        for i in range(TELEMETRY_QUOTA_PER_HOUR):
            c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1))
        assert c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1)) is False

    def test_quota_per_installation(self):
        c = AppTelemetryCollector()
        for i in range(TELEMETRY_QUOTA_PER_HOUR):
            c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1))
        # inst-2 still has quota
        assert c.record_metric("inst-2", TelemetryMetric("m", MetricKind.COUNTER, 1)) is True

    def test_quota_shared_across_types(self):
        c = AppTelemetryCollector()
        for i in range(TELEMETRY_QUOTA_PER_HOUR - 1):
            c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1))
        # Last slot used by an error
        assert c.report_error("inst-1", ErrorReport("E", "msg")) is True
        # Now over quota for spans too
        assert c.record_span("inst-1", PerformanceSpan("op", 10)) is False


class TestSummary:
    def test_summary_counts(self):
        c = AppTelemetryCollector()
        c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1))
        c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 2))
        c.report_error("inst-1", ErrorReport("E", "msg"))
        c.record_span("inst-1", PerformanceSpan("op", 50))
        s = c.get_summary("inst-1")
        assert s.total_metrics == 2
        assert s.total_errors == 1
        assert s.total_spans == 1

    def test_error_rate(self):
        c = AppTelemetryCollector()
        for _ in range(9):
            c.record_metric("inst-1", TelemetryMetric("m", MetricKind.COUNTER, 1))
        c.report_error("inst-1", ErrorReport("E", "msg"))
        s = c.get_summary("inst-1")
        assert s.error_rate == 10.0  # 1/10 = 10%

    def test_avg_span(self):
        c = AppTelemetryCollector()
        c.record_span("inst-1", PerformanceSpan("op", 100))
        c.record_span("inst-1", PerformanceSpan("op", 200))
        s = c.get_summary("inst-1")
        assert s.avg_span_ms == 150.0

    def test_top_errors(self):
        c = AppTelemetryCollector()
        for _ in range(5):
            c.report_error("inst-1", ErrorReport("ValueError", "bad"))
        for _ in range(2):
            c.report_error("inst-1", ErrorReport("TimeoutError", "slow"))
        s = c.get_summary("inst-1")
        assert s.top_errors[0] == ("ValueError", 5)
        assert s.top_errors[1] == ("TimeoutError", 2)

    def test_top_slow_ops(self):
        c = AppTelemetryCollector()
        c.record_span("inst-1", PerformanceSpan("fast", 10))
        c.record_span("inst-1", PerformanceSpan("slow", 500))
        s = c.get_summary("inst-1")
        assert s.top_slow_ops[0][0] == "slow"

    def test_empty_summary(self):
        c = AppTelemetryCollector()
        s = c.get_summary("inst-x")
        assert s.total_metrics == 0
        assert s.error_rate == 0
        assert s.avg_span_ms == 0
