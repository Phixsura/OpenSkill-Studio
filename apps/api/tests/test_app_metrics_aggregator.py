"""Tests for App Metrics Aggregator — record, aggregate, buckets, labels."""

import math

import pytest

from app.services.app_metrics_aggregator import (
    AggregationType,
    AppMetricsAggregator,
    BucketSize,
)


class TestRecord:
    def test_record(self):
        m = AppMetricsAggregator()
        p = m.record("inst-1", "latency_ms", 42.5, now=1000.0)
        assert p.value == 42.5

    def test_with_labels(self):
        m = AppMetricsAggregator()
        p = m.record("inst-1", "requests", 1, labels={"method": "GET"})
        assert p.labels["method"] == "GET"

    def test_nan_rejected(self):
        m = AppMetricsAggregator()
        with pytest.raises(ValueError, match="finite"):
            m.record("inst-1", "x", float("nan"))

    def test_inf_rejected(self):
        m = AppMetricsAggregator()
        with pytest.raises(ValueError, match="finite"):
            m.record("inst-1", "x", float("inf"))

    def test_missing_metric(self):
        m = AppMetricsAggregator()
        with pytest.raises(ValueError, match="metric"):
            m.record("inst-1", "", 1.0)


class TestAggregate:
    def test_sum(self):
        m = AppMetricsAggregator()
        for v in [10, 20, 30]:
            m.record("inst-1", "req", v, now=1000.0)
        r = m.aggregate("inst-1", "req", AggregationType.SUM)
        assert r.value == 60
        assert r.count == 3

    def test_avg(self):
        m = AppMetricsAggregator()
        for v in [10, 20, 30]:
            m.record("inst-1", "req", v, now=1000.0)
        r = m.aggregate("inst-1", "req", AggregationType.AVG)
        assert r.value == 20.0

    def test_min_max(self):
        m = AppMetricsAggregator()
        for v in [5, 15, 10]:
            m.record("inst-1", "lat", v, now=1000.0)
        assert m.aggregate("inst-1", "lat", AggregationType.MIN).value == 5
        assert m.aggregate("inst-1", "lat", AggregationType.MAX).value == 15

    def test_count(self):
        m = AppMetricsAggregator()
        for _ in range(7):
            m.record("inst-1", "hits", 1, now=1000.0)
        r = m.aggregate("inst-1", "hits", AggregationType.COUNT)
        assert r.value == 7.0

    def test_p99(self):
        m = AppMetricsAggregator()
        for v in range(1, 101):
            m.record("inst-1", "lat", float(v), now=1000.0)
        r = m.aggregate("inst-1", "lat", AggregationType.P99)
        assert r.value == 99.0

    def test_empty_metric(self):
        m = AppMetricsAggregator()
        r = m.aggregate("inst-1", "nothing", AggregationType.SUM)
        assert r.value == 0.0
        assert r.count == 0


class TestTimeFilter:
    def test_since(self):
        m = AppMetricsAggregator()
        m.record("inst-1", "req", 1, now=1000.0)
        m.record("inst-1", "req", 2, now=2000.0)
        r = m.aggregate("inst-1", "req", AggregationType.SUM, since=1500.0)
        assert r.value == 2

    def test_until(self):
        m = AppMetricsAggregator()
        m.record("inst-1", "req", 1, now=1000.0)
        m.record("inst-1", "req", 2, now=2000.0)
        r = m.aggregate("inst-1", "req", AggregationType.SUM, until=1500.0)
        assert r.value == 1


class TestLabelFilter:
    def test_filter_by_label(self):
        m = AppMetricsAggregator()
        m.record("inst-1", "req", 1, labels={"method": "GET"}, now=1000.0)
        m.record("inst-1", "req", 1, labels={"method": "POST"}, now=1000.0)
        r = m.aggregate("inst-1", "req", AggregationType.COUNT,
                         label_filter={"method": "GET"})
        assert r.value == 1.0


class TestBuckets:
    def test_hourly_buckets(self):
        m = AppMetricsAggregator()
        # 2026-10-28 10:00 and 11:00 UTC
        m.record("inst-1", "req", 5, now=1793167200.0)   # 10:00
        m.record("inst-1", "req", 3, now=1793167200.0)   # 10:00
        m.record("inst-1", "req", 7, now=1793170800.0)   # 11:00
        results = m.aggregate_by_bucket(
            "inst-1", "req", AggregationType.SUM, BucketSize.HOUR)
        assert len(results) == 2
        assert results[0].value == 8
        assert results[1].value == 7


class TestListMetrics:
    def test_list(self):
        m = AppMetricsAggregator()
        m.record("inst-1", "latency", 1)
        m.record("inst-1", "requests", 1)
        assert set(m.list_metrics("inst-1")) == {"latency", "requests"}


class TestIsolation:
    def test_cross_installation(self):
        m = AppMetricsAggregator()
        m.record("inst-1", "req", 10, now=1000.0)
        r = m.aggregate("inst-2", "req", AggregationType.SUM)
        assert r.count == 0
