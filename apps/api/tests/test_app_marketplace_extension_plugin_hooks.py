from app.services.app_marketplace_extension_plugin_hooks import (
    PluginHooksService, HookPoint,
)


def test_register_and_execute():
    svc = PluginHooksService()
    svc.register("ext-1", HookPoint.POST_INSTALL, "setup_db")
    results = svc.execute("ext-1", HookPoint.POST_INSTALL)
    assert len(results) == 1
    assert results[0].success is True
    assert results[0].handler_name == "setup_db"


def test_priority_ordering():
    svc = PluginHooksService()
    svc.register("ext-1", HookPoint.PRE_ACTIVATE, "low_priority", priority=1)
    svc.register("ext-1", HookPoint.PRE_ACTIVATE, "high_priority", priority=10)
    results = svc.execute("ext-1", HookPoint.PRE_ACTIVATE)
    assert results[0].handler_name == "high_priority"


def test_error_auto_disable():
    svc = PluginHooksService()
    hook = svc.register("ext-1", HookPoint.ON_ERROR, "flaky_handler")
    hook.max_errors = 3
    for _ in range(3):
        svc.record_error(hook.hook_id, "timeout")
    assert hook.enabled is False


def test_disable_enable():
    svc = PluginHooksService()
    hook = svc.register("ext-1", HookPoint.POST_INSTALL, "handler")
    svc.disable(hook.hook_id)
    results = svc.execute("ext-1", HookPoint.POST_INSTALL)
    assert len(results) == 0
    svc.enable(hook.hook_id)
    results2 = svc.execute("ext-1", HookPoint.POST_INSTALL)
    assert len(results2) == 1


def test_unregister():
    svc = PluginHooksService()
    hook = svc.register("ext-1", HookPoint.PRE_UNINSTALL, "cleanup")
    assert svc.unregister(hook.hook_id) is True
    assert len(svc.list_hooks("ext-1")) == 0


def test_list_by_point():
    svc = PluginHooksService()
    svc.register("ext-1", HookPoint.PRE_INSTALL, "a")
    svc.register("ext-1", HookPoint.POST_INSTALL, "b")
    svc.register("ext-1", HookPoint.PRE_INSTALL, "c")
    hooks = svc.list_hooks("ext-1", HookPoint.PRE_INSTALL)
    assert len(hooks) == 2


def test_no_hooks_returns_empty():
    svc = PluginHooksService()
    results = svc.execute("ext-x", HookPoint.POST_ACTIVATE)
    assert results == []
