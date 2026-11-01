from app.services.app_marketplace_app_app_app_app_app_app_app_announcement import AnnouncementManager

def test_announcements():
    mgr = AnnouncementManager()
    a1 = mgr.create(title="New Feature!", body="Check out SSO", variant="success")
    a2 = mgr.create(title="Maintenance", body="Scheduled downtime", variant="warning")
    active = mgr.get_active(user_id="u1")
    assert len(active) == 2
    mgr.dismiss(a1["id"], "u1")
    active2 = mgr.get_active(user_id="u1")
    assert len(active2) == 1
    mgr.deactivate(a2["id"])
    assert len(mgr.get_active(user_id="u1")) == 0
