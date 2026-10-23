from app.services.app_marketplace_notification_inbox import get_inbox, mark_read, mark_all_read, group_by_date

def test_inbox():
    notifs = [{"id": "n1", "read": False, "created_at": "2026-01-02", "category": "install"},
              {"id": "n2", "read": True, "created_at": "2026-01-01", "category": "review"}]
    r = get_inbox(notifications=notifs)
    assert r["unread"] == 1
    assert r["showing"] == 2

def test_unread_only():
    notifs = [{"id": "n1", "read": False}, {"id": "n2", "read": True}]
    r = get_inbox(notifications=notifs, unread_only=True)
    assert r["showing"] == 1

def test_mark_read():
    notifs = [{"id": "n1", "read": False}, {"id": "n2", "read": False}]
    r = mark_read(notification_id="n1", notifications=notifs)
    assert r[0]["read"]
    assert not r[1]["read"]

def test_mark_all():
    notifs = [{"id": "n1", "read": False}, {"id": "n2", "read": False}]
    r = mark_all_read(notifications=notifs)
    assert all(n["read"] for n in r)

def test_group():
    notifs = [{"created_at": "2026-01-01T10:00:00Z"}, {"created_at": "2026-01-01T11:00:00Z"},
              {"created_at": "2026-01-02T10:00:00Z"}]
    g = group_by_date(notifications=notifs)
    assert len(g) == 2
    assert g[0]["date"] == "2026-01-02"
