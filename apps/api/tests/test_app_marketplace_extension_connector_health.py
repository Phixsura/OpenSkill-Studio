from app.services.app_marketplace_extension_connector_health import (
    ConnectorHealthService, HealthStatus,
)
import pytest


def test_healthy_check():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com/health")
    check = svc.record_check("conn-1", response_time_ms=150, status_code=200)
    assert check.status == HealthStatus.HEALTHY
    assert svc.get_status("conn-1") == HealthStatus.HEALTHY


def test_degraded_check():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com", degraded_threshold_ms=500)
    check = svc.record_check("conn-1", response_time_ms=800, status_code=200)
    assert check.status == HealthStatus.DEGRADED


def test_down_on_error():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com")
    check = svc.record_check("conn-1", response_time_ms=0, error="connection refused")
    assert check.status == HealthStatus.DOWN


def test_consecutive_failures():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com", check_interval=30)
    svc._configs["conn-1"].failure_threshold = 2
    svc.record_check("conn-1", 0, 500)
    svc.record_check("conn-1", 0, 500)
    assert svc.get_status("conn-1") == HealthStatus.DOWN


def test_uptime():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com")
    for _ in range(9):
        svc.record_check("conn-1", 100, 200)
    svc.record_check("conn-1", 0, error="timeout")
    uptime = svc.get_uptime("conn-1")
    assert uptime["uptime_percent"] == 90.0
    assert uptime["healthy"] == 9


def test_sla_check():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com")
    for _ in range(99):
        svc.record_check("conn-1", 50, 200)
    svc.record_check("conn-1", 0, error="down")
    sla = svc.check_sla("conn-1", target_uptime=99.9)
    assert sla["meets_sla"] is False
    assert sla["gap"] > 0


def test_avg_response_time():
    svc = ConnectorHealthService()
    svc.configure("conn-1", "https://api.example.com")
    svc.record_check("conn-1", 100, 200)
    svc.record_check("conn-1", 200, 200)
    assert svc.get_avg_response_time("conn-1") == 150.0
