from app.services.app_marketplace_extension_uptime_monitor import PlatformUptimeMonitorService


def test_check_up():
    svc = PlatformUptimeMonitorService()
    for _ in range(100):
        svc.check("api", True)
    result = svc.get_uptime("api")
    assert result["uptime_pct"] == 100.0
    assert result["sla_9999"] is True


def test_check_with_downtime():
    svc = PlatformUptimeMonitorService()
    for _ in range(99):
        svc.check("api", True)
    svc.check("api", False)
    result = svc.get_uptime("api")
    assert result["uptime_pct"] == 99.0
    assert result["sla_999"] is False


def test_streak():
    svc = PlatformUptimeMonitorService()
    for _ in range(50):
        svc.check("api", True)
    svc.check("api", False)
    for _ in range(10):
        svc.check("api", True)
    result = svc.get_uptime("api")
    assert result["longest_streak"] == 50
    assert result["current_streak"] == 10


def test_overall():
    svc = PlatformUptimeMonitorService()
    for _ in range(100):
        svc.check("api", True)
        svc.check("db", True)
    svc.check("db", False)
    overall = svc.get_overall()
    assert overall["services"] == 2
    assert overall["all_healthy"] is False
