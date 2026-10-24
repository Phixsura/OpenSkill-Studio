from app.services.app_marketplace_app_app_app_app_app_app_app_change_mgmt import ChangeTracker

def test_full_flow():
    ct = ChangeTracker()
    ct.create("c1", "Update DNS", "low", "alice")
    ct.submit("c1")
    r = ct.approve("c1", "bob")
    assert r["status"] == "approved"
    r2 = ct.implement("c1")
    assert r2["success"]

def test_high_risk():
    ct = ChangeTracker()
    ct.create("c2", "DB migration", "high", "alice")
    ct.submit("c2")
    r1 = ct.approve("c2", "bob")
    assert r1["status"] == "pending_review"
    r2 = ct.approve("c2", "carol")
    assert r2["status"] == "approved"

def test_not_approved():
    ct = ChangeTracker()
    ct.create("c3", "Test", "low", "alice")
    r = ct.implement("c3")
    assert not r["success"]
