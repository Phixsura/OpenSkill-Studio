from app.services.app_upgrade_planner import plan_batch_upgrade

INSTALLS = [{"id": "i1", "auto_upgrade": True}, {"id": "i2", "auto_upgrade": True}, {"id": "i3", "auto_upgrade": False}]

def test_no_new_perms():
    p = plan_batch_upgrade(INSTALLS, target_version="2.0", new_permissions=[])
    assert p["auto_upgrade"] == 2
    assert p["manual_upgrade"] == 1

def test_with_new_perms():
    p = plan_batch_upgrade(INSTALLS, target_version="2.0", new_permissions=["write:cohorts"])
    assert p["needs_consent"] is True
    assert p["auto_upgrade"] == 0  # all need consent

def test_empty():
    p = plan_batch_upgrade([], target_version="1.0", new_permissions=[])
    assert p["total"] == 0
