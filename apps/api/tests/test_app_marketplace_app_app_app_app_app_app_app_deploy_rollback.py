from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_rollback import RollbackManager

def test_deploy_rollback():
    mgr = RollbackManager()
    mgr.deploy(version="1.0.0", commit="abc123", deployer="alice")
    mgr.deploy(version="1.1.0", commit="def456", deployer="bob")
    mgr.deploy(version="1.2.0", commit="ghi789", deployer="alice")
    h = mgr.history()
    assert h["current"] == "1.2.0"
    assert h["total"] == 3
    r = mgr.rollback()
    assert r["rolled_back_to"] == "1.1.0"
    assert r["from"] == "1.2.0"
    h2 = mgr.history()
    assert h2["current"] == "1.1.0"
    assert h2["total"] == 4

def test_no_rollback():
    mgr = RollbackManager()
    mgr.deploy(version="1.0.0", commit="x", deployer="a")
    r = mgr.rollback()
    assert "error" in r
