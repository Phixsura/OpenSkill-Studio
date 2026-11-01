from app.services.app_marketplace_extension_health_check import (
    HealthCheckService, HealthProbe, ProbeType, ProbeResult,
)


def test_register_and_success():
    hcs = HealthCheckService()
    hcs.register_probe(HealthProbe("p1", "ext-1", ProbeType.LIVENESS, "/health"))
    result = hcs.record_execution("p1", ProbeResult.SUCCESS, 25.0)
    assert result["healthy"] is True
    assert result["consecutive_failures"] == 0


def test_failure_threshold():
    hcs = HealthCheckService()
    hcs.register_probe(HealthProbe("p2", "ext-2", ProbeType.READINESS, "/ready",
                                    failure_threshold=3))
    hcs.record_execution("p2", ProbeResult.FAILURE)
    hcs.record_execution("p2", ProbeResult.FAILURE)
    r = hcs.record_execution("p2", ProbeResult.FAILURE)
    assert r["failed_threshold"] is True
    assert r["consecutive_failures"] == 3


def test_recovery():
    hcs = HealthCheckService()
    hcs.register_probe(HealthProbe("p3", "ext-3", ProbeType.LIVENESS, "/health"))
    hcs.record_execution("p3", ProbeResult.FAILURE)
    hcs.record_execution("p3", ProbeResult.FAILURE)
    hcs.record_execution("p3", ProbeResult.SUCCESS)
    r = hcs.record_execution("p3", ProbeResult.SUCCESS)
    assert r["consecutive_failures"] == 0
    assert r["healthy"] is True


def test_probe_status():
    hcs = HealthCheckService()
    hcs.register_probe(HealthProbe("p4", "ext-4", ProbeType.STARTUP, "/startup"))
    hcs.record_execution("p4", ProbeResult.SUCCESS, 42.0)
    status = hcs.get_probe_status("p4")
    assert status["last_result"] == "success"
    assert status["last_response_ms"] == 42.0
    assert status["total_checks"] == 1


def test_extension_health():
    hcs = HealthCheckService()
    hcs.register_probe(HealthProbe("live", "ext-5", ProbeType.LIVENESS, "/health"))
    hcs.register_probe(HealthProbe("ready", "ext-5", ProbeType.READINESS, "/ready"))
    hcs.record_execution("live", ProbeResult.SUCCESS)
    hcs.record_execution("ready", ProbeResult.SUCCESS)
    health = hcs.get_extension_health("ext-5")
    assert health["overall"] == "healthy"
    assert len(health["probes"]) == 2


def test_unhealthy_extension():
    hcs = HealthCheckService()
    hcs.register_probe(HealthProbe("p6", "ext-6", ProbeType.LIVENESS, "/h"))
    hcs.record_execution("p6", ProbeResult.FAILURE)
    health = hcs.get_extension_health("ext-6")
    assert health["overall"] == "unhealthy"
