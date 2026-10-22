from app.services.app_marketplace_notification_center import (
    build_notification, create_from_template, get_unread_count, mark_all_read,
)

def test_build():
    n = build_notification(type="info", title="Hi", message="Hello")
    assert not n["read"]
    assert n["type"] == "info"

def test_template_install():
    n = create_from_template(type="new_install", params={"app_name": "MyApp", "org_name": "Acme"})
    assert "MyApp" in n["message"]
    assert "Acme" in n["message"]

def test_template_unknown():
    assert create_from_template(type="unknown", params={}) is None

def test_unread_count():
    notifs = [{"read": False}, {"read": True}, {"read": False}]
    assert get_unread_count(notifications=notifs) == 2

def test_mark_all():
    notifs = [{"read": False, "type": "a"}, {"read": False, "type": "b"}]
    result = mark_all_read(notifications=notifs)
    assert all(n["read"] for n in result)
