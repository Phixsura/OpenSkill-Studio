from app.services.app_marketplace_extension_install_flow import ExtInstallFlowService

def test_full_flow():
    svc = ExtInstallFlowService()
    s = svc.start("ext-1", "u1")
    assert s.step == "consent"
    svc.grant_permissions(s.session_id, ["read:data"])
    assert s.step == "configure"
    svc.set_config(s.session_id, {"key": "val"})
    assert s.step == "install"
    svc.complete(s.session_id)
    assert s.step == "complete"
    assert svc.is_installed("u1", "ext-1") is True

def test_no_duplicate_install():
    svc = ExtInstallFlowService()
    s = svc.start("ext-1", "u1")
    svc.grant_permissions(s.session_id, [])
    svc.set_config(s.session_id, {})
    svc.complete(s.session_id)
    try:
        svc.start("ext-1", "u1")
        assert False
    except ValueError:
        pass

def test_uninstall():
    svc = ExtInstallFlowService()
    s = svc.start("ext-1", "u1")
    svc.grant_permissions(s.session_id, [])
    svc.set_config(s.session_id, {})
    svc.complete(s.session_id)
    assert svc.uninstall("u1", "ext-1") is True
    assert svc.is_installed("u1", "ext-1") is False

def test_fail():
    svc = ExtInstallFlowService()
    s = svc.start("ext-1", "u1")
    svc.fail(s.session_id, "Network error")
    assert s.step == "failed"
