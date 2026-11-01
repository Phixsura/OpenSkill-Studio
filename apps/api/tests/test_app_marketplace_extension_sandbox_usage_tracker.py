from app.services.app_marketplace_extension_sandbox_usage_tracker import (
    SandboxUsageTrackerService,
)


def test_record_and_get():
    svc = SandboxUsageTrackerService()
    svc.record("sb-1", cpu=50, memory_mb=128, api_calls=10)
    buckets = svc.get_usage("sb-1", last_minutes=5)
    assert len(buckets) == 1
    assert buckets[0].cpu_percent == 50


def test_merge_same_bucket():
    svc = SandboxUsageTrackerService()
    svc.record("sb-1", cpu=50, api_calls=5)
    svc.record("sb-1", cpu=80, api_calls=3)
    buckets = svc.get_usage("sb-1")
    assert len(buckets) == 1
    assert buckets[0].cpu_percent == 80  # max
    assert buckets[0].api_calls == 8  # sum


def test_peaks():
    svc = SandboxUsageTrackerService()
    svc.record("sb-1", cpu=30, memory_mb=100)
    svc.record("sb-1", cpu=90, memory_mb=200)
    svc.record("sb-1", cpu=50, memory_mb=150)
    peaks = svc.get_peaks("sb-1")
    assert peaks["cpu"] == 90
    assert peaks["memory_mb"] == 200


def test_averages():
    svc = SandboxUsageTrackerService()
    svc.record("sb-1", cpu=40)
    svc.record("sb-1", cpu=60)
    avgs = svc.get_averages("sb-1")
    assert avgs["cpu"] == 60.0  # merged bucket, max is 60


def test_totals():
    svc = SandboxUsageTrackerService()
    svc.record("sb-1", api_calls=100, network_bytes=5000)
    svc.record("sb-1", api_calls=50, network_bytes=3000)
    totals = svc.get_totals("sb-1")
    assert totals["api_calls"] == 150
    assert totals["network_bytes"] == 8000


def test_forecast():
    svc = SandboxUsageTrackerService()
    # Create multiple buckets by setting different timestamps
    for i in range(5):
        b = svc.record("sb-1", api_calls=10)
        b.timestamp -= (i + 1) * 61  # force different buckets
    fc = svc.forecast("sb-1", "api_calls", 60)
    assert fc["forecast"] > 0


def test_empty_sandbox():
    svc = SandboxUsageTrackerService()
    assert svc.get_usage("empty") == []
    assert svc.get_peaks("empty")["cpu"] == 0
    assert svc.get_averages("empty")["cpu"] == 0
