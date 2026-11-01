from app.services.app_marketplace_resource_monitor import ResourceMonitor


def test_record_and_latest():
    rm = ResourceMonitor()
    rm.record_sample("ext-1", 25.0, 128.0, 10, 5000)
    rm.record_sample("ext-1", 30.0, 140.0, 15, 6000)
    latest = rm.get_latest("ext-1")
    assert latest is not None
    assert latest.cpu_percent == 30.0
    assert latest.memory_mb == 140.0


def test_averages():
    rm = ResourceMonitor()
    rm.record_sample("ext-2", 20.0, 100.0)
    rm.record_sample("ext-2", 40.0, 200.0)
    rm.record_sample("ext-2", 60.0, 300.0)
    avg = rm.get_averages("ext-2")
    assert avg["cpu"] == 40.0
    assert avg["memory"] == 200.0
    assert avg["sample_count"] == 3


def test_peaks():
    rm = ResourceMonitor()
    rm.record_sample("ext-3", 10.0, 50.0)
    rm.record_sample("ext-3", 95.0, 400.0)
    rm.record_sample("ext-3", 30.0, 100.0)
    peaks = rm.get_peaks("ext-3")
    assert peaks["cpu"] == 95.0
    assert peaks["memory"] == 400.0


def test_alerts():
    rm = ResourceMonitor(alert_cpu=80.0, alert_memory_mb=256.0)
    rm.record_sample("ext-4", 85.0, 100.0)
    rm.record_sample("ext-4", 50.0, 300.0)
    alerts = rm.get_alerts("ext-4")
    assert len(alerts) == 2
    assert alerts[0]["type"] == "cpu_high"
    assert alerts[1]["type"] == "memory_high"


def test_trend():
    rm = ResourceMonitor()
    # First 10 samples: low CPU
    for _ in range(10):
        rm.record_sample("ext-5", 20.0, 100.0)
    # Next 10 samples: high CPU
    for _ in range(10):
        rm.record_sample("ext-5", 80.0, 100.0)
    trend = rm.get_trend("ext-5", "cpu", window=10)
    assert trend == "increasing"


def test_clear():
    rm = ResourceMonitor()
    rm.record_sample("ext-6", 50.0, 200.0)
    rm.record_sample("ext-6", 60.0, 250.0)
    cleared = rm.clear_samples("ext-6")
    assert cleared == 2
    assert rm.get_latest("ext-6") is None
