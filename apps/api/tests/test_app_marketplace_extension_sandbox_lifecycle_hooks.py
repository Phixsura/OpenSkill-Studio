from app.services.app_marketplace_extension_sandbox_lifecycle_hooks import (
    SandboxLifecycleHooksService, LifecycleEvent,
)
import pytest


def test_register_and_trigger():
    svc = SandboxLifecycleHooksService()
    svc.register("sb-1", LifecycleEvent.AFTER_START, "init_db")
    results = svc.trigger("sb-1", LifecycleEvent.AFTER_START)
    assert len(results) == 1
    assert results[0].success is True


def test_ordering():
    svc = SandboxLifecycleHooksService()
    svc.register("sb-1", LifecycleEvent.BEFORE_STOP, "save_state", order=2)
    svc.register("sb-1", LifecycleEvent.BEFORE_STOP, "flush_cache", order=1)
    hooks = svc.list_hooks("sb-1", LifecycleEvent.BEFORE_STOP)
    assert hooks[0].handler_name == "flush_cache"
    assert hooks[1].handler_name == "save_state"


def test_error_auto_disable():
    svc = SandboxLifecycleHooksService()
    hook = svc.register("sb-1", LifecycleEvent.ON_CRASH, "report")
    for _ in range(5):
        svc.record_error(hook.hook_id, "sb-1", "handler failed")
    assert hook.enabled is False


def test_unregister():
    svc = SandboxLifecycleHooksService()
    hook = svc.register("sb-1", LifecycleEvent.AFTER_START, "init")
    assert svc.unregister("sb-1", hook.hook_id) is True
    assert len(svc.list_hooks("sb-1")) == 0


def test_disabled_not_triggered():
    svc = SandboxLifecycleHooksService()
    hook = svc.register("sb-1", LifecycleEvent.AFTER_START, "init")
    hook.enabled = False
    results = svc.trigger("sb-1", LifecycleEvent.AFTER_START)
    assert len(results) == 0


def test_max_hooks():
    svc = SandboxLifecycleHooksService()
    for i in range(20):
        svc.register("sb-1", LifecycleEvent.ON_HEALTH_CHECK, f"check_{i}")
    with pytest.raises(ValueError, match="Max hooks"):
        svc.register("sb-1", LifecycleEvent.ON_HEALTH_CHECK, "overflow")


def test_stats():
    svc = SandboxLifecycleHooksService()
    svc.register("sb-1", LifecycleEvent.AFTER_START, "init")
    svc.register("sb-1", LifecycleEvent.BEFORE_STOP, "cleanup")
    svc.trigger("sb-1", LifecycleEvent.AFTER_START)
    stats = svc.get_stats("sb-1")
    assert stats["total"] == 2
    assert stats["total_executions"] == 1


def test_multiple_events():
    svc = SandboxLifecycleHooksService()
    svc.register("sb-1", LifecycleEvent.BEFORE_START, "pre")
    svc.register("sb-1", LifecycleEvent.AFTER_START, "post")
    svc.register("sb-1", LifecycleEvent.ON_CRASH, "crash")
    assert len(svc.list_hooks("sb-1")) == 3
    assert len(svc.list_hooks("sb-1", LifecycleEvent.ON_CRASH)) == 1
