from app.services.app_marketplace_app_developer_inbox import create_message, get_inbox_summary

def test_create():
    r = create_message(msg_type="review", title="New 5-star review!", body="Great app", app_id="a1")
    assert r["message_id"].startswith("msg_")
    assert r["icon"] == "⭐"
    assert not r["read"]

def test_summary():
    messages = [
        {"type": "review", "read": True},
        {"type": "security", "read": False},
        {"type": "support", "read": False},
        {"type": "install", "read": False},
    ]
    r = get_inbox_summary(messages=messages)
    assert r["unread"] == 3
    assert r["priority_unread"] == 2
    assert r["by_type"]["review"] == 1
