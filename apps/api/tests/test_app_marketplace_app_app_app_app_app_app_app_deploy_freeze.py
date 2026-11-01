from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_freeze import DeployFreezeController
import time

def test_freeze():
    dfc = DeployFreezeController()
    dfc.create_freeze("Black Friday", 48, "ops-lead")
    r = dfc.is_frozen()
    assert r["frozen"]
    assert r["remaining_hours"] > 0

def test_lift():
    dfc = DeployFreezeController()
    dfc.create_freeze("Maintenance", 2, "admin")
    dfc.lift_freeze()
    assert not dfc.is_frozen()["frozen"]

def test_expired():
    dfc = DeployFreezeController()
    dfc.create_freeze("test", 1, "admin")
    r = dfc.is_frozen(now=time.time() + 7200)
    assert not r["frozen"]
