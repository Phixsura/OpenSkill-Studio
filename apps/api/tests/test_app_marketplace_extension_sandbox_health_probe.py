from app.services.app_marketplace_extension_sandbox_health_probe import (
    SandboxHealthProbeService, ProbeType,
)


def test_configure_and_record():
    svc = SandboxHealthProbeService()
    svc.configure("sb-1", ProbeType.LIVENESS)
    check = svc.record("sb-1", ProbeType.LIVENESS, True, latency_ms=5)
    assert check.result.value == "pass"
    assert svc.is_healthy("sb-1", ProbeType.LIVENESS) is True


def test_failure_threshold():
    svc = SandboxHealthProbeService()
    svc.configure("sb-1", ProbeType.LIVENESS, failure_threshold=3)
    svc.record("sb-1", ProbeType.LIVENESS, False)
    svc.record("sb-1", ProbeType.LIVENESS, False)
    assert svc.is_healthy("sb-1", ProbeType.LIVENESS) is True  # not yet
    svc.record("sb-1", ProbeType.LIVENESS, False)
    assert svc.is_healthy("sb-1", ProbeType.LIVENESS) is False


def test_readiness_probe():
    svc = SandboxHealthProbeService()
    svc.configure("sb-1", ProbeType.READINESS, failure_threshold=2)
    svc.record("sb-1", ProbeType.READINESS, False)
    svc.record("sb-1", ProbeType.READINESS, False)
    assert svc.is_healthy("sb-1", ProbeType.READINESS) is False


def test_get_status():
    svc = SandboxHealthProbeService()
    svc.configure("sb-1", ProbeType.LIVENESS)
    svc.configure("sb-1", ProbeType.READINESS)
    svc.record("sb-1", ProbeType.LIVENESS, True)
    svc.record("sb-1", ProbeType.READINESS, True)
    status = svc.get_status("sb-1")
    assert "liveness" in status
    assert "readiness" in status
    assert status["liveness"]["healthy"] is True


def test_history():
    svc = SandboxHealthProbeService()
    svc.configure("sb-1", ProbeType.LIVENESS)
    for _ in range(5):
        svc.record("sb-1", ProbeType.LIVENESS, True, latency_ms=10)
    history = svc.get_history("sb-1", ProbeType.LIVENESS)
    assert len(history) == 5


def test_startup_probe():
    svc = SandboxHealthProbeService()
    svc.configure("sb-1", ProbeType.STARTUP, failure_threshold=5)
    for _ in range(4):
        svc.record("sb-1", ProbeType.STARTUP, False)
    assert svc.is_healthy("sb-1", ProbeType.STARTUP) is True  # not yet at 5
    svc.record("sb-1", ProbeType.STARTUP, False)
    assert svc.is_healthy("sb-1", ProbeType.STARTUP) is False
