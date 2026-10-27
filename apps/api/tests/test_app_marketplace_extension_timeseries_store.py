from app.services.app_marketplace_extension_timeseries_store import TimeSeriesStoreService
import time


def test_record_and_query():
    ts = TimeSeriesStoreService()
    base = time.time()
    ts.record("cpu", 50.0, base)
    ts.record("cpu", 60.0, base + 1)
    ts.record("cpu", 70.0, base + 2)
    points = ts.query("cpu", base, base + 2)
    assert len(points) == 3
    assert points[0].value == 50.0


def test_aggregate_avg():
    ts = TimeSeriesStoreService()
    base = 1000000.0
    for i in range(10):
        ts.record("mem", float(i * 10), base + i)
    result = ts.aggregate("mem", base, base + 10, func="avg", bucket_seconds=5)
    assert len(result) == 2  # 2 buckets of 5 seconds
    assert result[0]["value"] == 20.0  # avg of 0,10,20,30,40


def test_aggregate_max():
    ts = TimeSeriesStoreService()
    base = 2000000.0
    for i in range(5):
        ts.record("latency", float(i * 100), base + i)
    result = ts.aggregate("latency", base, base + 5, func="max", bucket_seconds=10)
    assert result[0]["value"] == 400.0


def test_aggregate_p99():
    ts = TimeSeriesStoreService()
    base = 3000000.0
    for i in range(100):
        ts.record("response_ms", float(i), base + i * 0.1)
    result = ts.aggregate("response_ms", base, base + 10, func="p99", bucket_seconds=20)
    assert result[0]["value"] >= 95  # p99 of 0..99


def test_rate():
    ts = TimeSeriesStoreService()
    base = 4000000.0
    ts.record("requests", 100.0, base)
    ts.record("requests", 200.0, base + 10)
    rate = ts.rate("requests", base, base + 10)
    assert rate == 10.0  # 100 increase over 10 seconds


def test_downsample():
    ts = TimeSeriesStoreService()
    base = time.time() - 7200  # 2 hours ago
    for i in range(100):
        ts.record("metric", float(i), base + i)
    original_count = len(ts._series["metric"])
    removed = ts.downsample("metric", older_than=3600, bucket_seconds=10)
    assert removed > 0
    assert len(ts._series["metric"]) < original_count


def test_latest():
    ts = TimeSeriesStoreService()
    ts.record("disk", 80.0, 1000.0)
    ts.record("disk", 85.0, 1001.0)
    assert ts.get_latest("disk").value == 85.0


def test_empty_metric():
    ts = TimeSeriesStoreService()
    assert ts.query("nonexistent", 0, 999999) == []
    assert ts.get_latest("nonexistent") is None
    assert ts.rate("nonexistent", 0, 100) == 0.0


def test_max_points_eviction():
    ts = TimeSeriesStoreService(max_points_per_metric=10)
    for i in range(20):
        ts.record("small", float(i), float(i))
    assert len(ts._series["small"]) == 10
    # Oldest should be evicted
    assert ts._series["small"][0].value == 10.0


def test_list_metrics():
    ts = TimeSeriesStoreService()
    ts.record("cpu", 1)
    ts.record("mem", 2)
    ts.record("disk", 3)
    assert ts.list_metrics() == ["cpu", "disk", "mem"]
