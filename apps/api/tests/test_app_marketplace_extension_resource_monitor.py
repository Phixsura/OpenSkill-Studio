from app.services.app_marketplace_extension_resource_monitor import (
    ResourceMonitorService, ResourceThresholds, AlertLevel,
)


def test_record_and_get():
    svc = ResourceMonitorService()
    svc.configure("sb-1", {"memory_mb": 256, "disk_mb": 512})
    svc.record("sb-1", cpu_percent=30, memory_mb=100, disk_mb=200)
    snap = svc.get_current("sb-1")
    assert snap is not None
    assert snap.cpu_percent == 30


def test_warning_alert():
    svc = ResourceMonitorService()
    svc.configure("sb-1", {"memory_mb": 256, "disk_mb": 512})
    alerts = svc.record("sb-1", cpu_percent=75, memory_mb=50, disk_mb=100)
    assert len(alerts) == 1
    assert alerts[0].resource == "cpu"
    assert alerts[0].level == AlertLevel.WARNING


def test_critical_throttle():
    svc = ResourceMonitorService()
    svc.configure("sb-1", {"memory_mb": 256, "disk_mb": 512})
    alerts = svc.record("sb-1", cpu_percent=95, memory_mb=50, disk_mb=100)
    assert any(a.level == AlertLevel.CRITICAL for a in alerts)
    assert svc.is_throttled("sb-1") is True


def test_unthrottle():
    svc = ResourceMonitorService()
    svc.configure("sb-1", {"memory_mb": 256, "disk_mb": 512})
    svc.record("sb-1", cpu_percent=95, memory_mb=50, disk_mb=100)
    assert svc.unthrottle("sb-1") is True
    assert svc.is_throttled("sb-1") is False


def test_history_limit():
    svc = ResourceMonitorService()
    svc.configure("sb-1", {"memory_mb": 256, "disk_mb": 512})
    for i in range(150):
        svc.record("sb-1", cpu_percent=i % 100, memory_mb=50, disk_mb=100)
    assert len(svc.get_history("sb-1")) == 50  # default limit
    assert len(svc._history["sb-1"]) == 100  # internal cap


def test_memory_alert():
    svc = ResourceMonitorService()
    svc.configure("sb-1", {"memory_mb": 100, "disk_mb": 512})
    alerts = svc.record("sb-1", cpu_percent=10, memory_mb=96, disk_mb=100)
    assert any(a.resource == "memory" and a.level == AlertLevel.CRITICAL for a in alerts)
