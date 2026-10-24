from app.services.app_marketplace_app_app_app_app_app_app_app_install_tracker import InstallTracker

def test_install():
    t = InstallTracker()
    t.install(app_id="slack", org_id="org1", user_id="alice")
    t.install(app_id="slack", org_id="org2", user_id="bob")
    t.install(app_id="github", org_id="org1", user_id="alice")
    assert t.is_installed(app_id="slack", org_id="org1")
    s = t.app_stats("slack")
    assert s["active_installs"] == 2
    t.uninstall(app_id="slack", org_id="org1")
    assert not t.is_installed(app_id="slack", org_id="org1")
    assert t.app_stats("slack")["active_installs"] == 1
    assert t.org_apps("org1") == ["github"]
