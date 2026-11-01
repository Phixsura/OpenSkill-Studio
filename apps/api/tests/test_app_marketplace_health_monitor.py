from app.services.app_marketplace_health_monitor import HealthMonitor, HealthStatus


def test_healthy_heartbeat():
    hm = HealthMonitor()
    check = hm.record_heartbeat("ext-1", 50.0)
    assert check.status == HealthStatus.HEALTHY
    assert hm.get_status("ext-1") == HealthStatus.HEALTHY


def test_degraded_heartbeat():
    hm = HealthMonitor(degraded_threshold=100.0)
    hm.record_heartbeat("ext-2", 500.0)
    assert hm.get_status("ext-2") == HealthStatus.DEGRADED


def test_unhealthy_on_error():
    hm = HealthMonitor()
    hm.record_heartbeat("ext-3", 10.0, error="Connection refused")
    assert hm.get_status("ext-3") == HealthStatus.UNHEALTHY


def test_error_rate():
    hm = HealthMonitor()
    hm.record_heartbeat("ext-4", 50.0)
    hm.record_heartbeat("ext-4", 50.0)
    hm.record_heartbeat("ext-4", 50.0, error="timeout")
    hm.record_heartbeat("ext-4", 50.0)
    rate = hm.get_error_rate("ext-4")
    assert rate == 0.25  # 1 error out of 4


def test_avg_response_time():
    hm = HealthMonitor()
    hm.record_heartbeat("ext-5", 100.0)
    hm.record_heartbeat("ext-5", 200.0)
    hm.record_heartbeat("ext-5", 300.0)
    avg = hm.get_avg_response_time("ext-5")
    assert avg == 200.0


def test_incidents_auto_created():
    hm = HealthMonitor()
    hm.record_heartbeat("ext-6", 10.0, error="crash")
    incidents = hm.get_incidents("ext-6")
    assert len(incidents) == 1
    assert incidents[0]["error"] == "crash"


def test_unknown_status():
    hm = HealthMonitor()
    assert hm.get_status("never-seen") == HealthStatus.UNKNOWN


def test_list_unhealthy():
    hm = HealthMonitor()
    hm.record_heartbeat("healthy-ext", 50.0)
    hm.record_heartbeat("sick-ext", 10.0, error="down")
    unhealthy = hm.list_unhealthy()
    assert "sick-ext" in unhealthy
    assert "healthy-ext" not in unhealthy
