from app.services.app_marketplace_app_app_app_app_app_app_app_res_lifecycle import ResourceLifecycleManager

def test_lifecycle():
    rlm = ResourceLifecycleManager()
    rlm.create("vm-1", "compute", "alice")
    rlm.update("vm-1", {"cpu": 4}, "alice")
    assert rlm.get("vm-1")["version"] == 2
    rlm.delete("vm-1", "admin")
    assert rlm.get("vm-1") is None
    s = rlm.stats()
    assert s["total"] == 0
    assert s["audit_entries"] == 3
