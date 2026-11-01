from app.services.app_marketplace_extension_sandbox_graceful_shutdown import (
    SandboxGracefulShutdownService, ShutdownPhase,
)


def test_initiate():
    svc = SandboxGracefulShutdownService()
    state = svc.initiate("sb-1")
    assert state.phase == ShutdownPhase.DRAINING
    assert svc.is_shutting_down("sb-1") is True


def test_full_lifecycle():
    svc = SandboxGracefulShutdownService()
    svc.initiate("sb-1")
    svc.record_hook("sb-1", True)
    svc.record_hook("sb-1", True)
    svc.complete_drain("sb-1")
    assert svc.get_state("sb-1").phase == ShutdownPhase.CLEANUP
    svc.record_cleanup("sb-1", "connections")
    svc.record_cleanup("sb-1", "timers")
    state = svc.terminate("sb-1")
    assert state.phase == ShutdownPhase.TERMINATED
    assert state.hooks_executed == 2
    assert len(state.resources_cleaned) == 2


def test_force_kill():
    svc = SandboxGracefulShutdownService()
    svc.initiate("sb-1")
    state = svc.force_kill("sb-1")
    assert state.phase == ShutdownPhase.FORCE_KILLED
    assert svc.is_shutting_down("sb-1") is False


def test_duration():
    svc = SandboxGracefulShutdownService()
    svc.initiate("sb-1")
    duration = svc.get_duration_ms("sb-1")
    assert duration >= 0


def test_hook_failure_tracking():
    svc = SandboxGracefulShutdownService()
    svc.initiate("sb-1")
    svc.record_hook("sb-1", True)
    svc.record_hook("sb-1", False)
    svc.record_hook("sb-1", True)
    state = svc.get_state("sb-1")
    assert state.hooks_executed == 3
    assert state.hooks_failed == 1


def test_not_shutting_down():
    svc = SandboxGracefulShutdownService()
    assert svc.is_shutting_down("sb-x") is False
