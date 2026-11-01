from app.services.app_marketplace_app_app_app_app_app_app_app_app_version_mgr import AppVersionManager

def test_versions():
    mgr = AppVersionManager()
    mgr.publish("app1", version="1.0.0", changelog="Initial release")
    mgr.publish("app1", version="1.1.0", changelog="Bug fixes")
    mgr.publish("app1", version="2.0.0", changelog="Major update")
    latest = mgr.get_latest("app1")
    assert latest["version"] == "2.0.0"
    versions = mgr.list_versions("app1")
    assert len(versions) == 3
    assert versions[0]["version"] == "2.0.0"
    mgr.rollback("app1", "1.1.0")
    assert mgr.get_latest("app1")["version"] == "1.1.0"
