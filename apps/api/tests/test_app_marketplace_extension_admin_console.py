from app.services.app_marketplace_extension_admin_console import ExtAdminConsoleService

def test_suspend():
    svc = ExtAdminConsoleService()
    svc.execute("admin-1", "suspend_extension", "extension", "ext-1", "ToS violation")
    assert svc.is_suspended("ext-1") is True
    svc.execute("admin-1", "unsuspend_extension", "extension", "ext-1")
    assert svc.is_suspended("ext-1") is False

def test_reason_required():
    svc = ExtAdminConsoleService()
    try:
        svc.execute("admin-1", "ban_developer", "developer", "dev-1")
        assert False
    except ValueError:
        pass

def test_feature():
    svc = ExtAdminConsoleService()
    svc.execute("admin-1", "feature_extension", "extension", "ext-1")
    assert "ext-1" in svc.get_featured()

def test_audit_log():
    svc = ExtAdminConsoleService()
    svc.execute("admin-1", "feature_extension", "extension", "ext-1")
    svc.execute("admin-1", "suspend_extension", "extension", "ext-2", "Spam")
    log = svc.get_audit_log()
    assert len(log) == 2
    assert log[0].action == "suspend_extension"
