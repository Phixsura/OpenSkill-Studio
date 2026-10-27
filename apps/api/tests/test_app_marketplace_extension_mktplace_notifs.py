from app.services.app_marketplace_extension_mktplace_notifs import MktplaceNotifsService

def test_send_and_get():
    svc = MktplaceNotifsService()
    svc.send("u1", "New install", "ext-1 installed", "install")
    svc.send("u1", "Update available", "ext-2 v2.0", "update")
    assert svc.get_unread_count("u1") == 2

def test_mark_read():
    svc = MktplaceNotifsService()
    n = svc.send("u1", "Review", "New 5-star review", "review")
    svc.mark_read("u1", n.notif_id)
    assert svc.get_unread_count("u1") == 0

def test_mark_all_read():
    svc = MktplaceNotifsService()
    svc.send("u1", "A", "a", "system")
    svc.send("u1", "B", "b", "system")
    count = svc.mark_all_read("u1")
    assert count == 2
    assert svc.get_unread_count("u1") == 0

def test_by_category():
    svc = MktplaceNotifsService()
    svc.send("u1", "Install", "x", "install")
    svc.send("u1", "Security", "y", "security")
    assert len(svc.get_by_category("u1", "security")) == 1
