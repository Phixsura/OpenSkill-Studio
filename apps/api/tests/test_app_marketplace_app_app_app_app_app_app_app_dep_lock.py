from app.services.app_marketplace_app_app_app_app_app_app_app_dep_lock import DependencyLockManager

def test_lock_unlock():
    dlm = DependencyLockManager()
    dlm.lock("api", "2.0.0", "release-manager")
    assert dlm.is_locked("api")
    r = dlm.check_upgrade("api", "2.1.0")
    assert not r["allowed"]
    dlm.unlock("api")
    assert not dlm.is_locked("api")
    r2 = dlm.check_upgrade("api", "2.1.0")
    assert r2["allowed"]
