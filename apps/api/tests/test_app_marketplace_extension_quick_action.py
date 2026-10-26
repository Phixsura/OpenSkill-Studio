from app.services.app_marketplace_extension_quick_action import ExtensionQuickActionService


def test_register_and_execute():
    svc = ExtensionQuickActionService()
    a = svc.register("ext-1", "Deploy", "🚀", "deploy_latest")
    result = svc.execute("ext-1", a.action_id)
    assert result["ok"] is True
    assert result["command"] == "deploy_latest"


def test_confirm_required():
    svc = ExtensionQuickActionService()
    a = svc.register("ext-1", "Reset DB", "💣", "reset_db", requires_confirm=True, dangerous=True)
    r1 = svc.execute("ext-1", a.action_id)
    assert r1["ok"] is False and r1["needs_confirm"]
    r2 = svc.execute("ext-1", a.action_id, confirmed=True)
    assert r2["ok"] is True


def test_cooldown():
    svc = ExtensionQuickActionService()
    a = svc.register("ext-1", "Restart", "🔄", "restart", cooldown_seconds=60)
    svc.execute("ext-1", a.action_id)
    r = svc.execute("ext-1", a.action_id)
    assert r["ok"] is False and "Cooldown" in r["error"]


def test_list_actions():
    svc = ExtensionQuickActionService()
    svc.register("ext-1", "Deploy", "🚀", "deploy")
    svc.register("ext-1", "Rollback", "⏪", "rollback")
    assert len(svc.list_actions("ext-1")) == 2
