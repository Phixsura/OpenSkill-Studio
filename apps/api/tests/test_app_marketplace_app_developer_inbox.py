from app.services.app_marketplace_app_developer_inbox import create_message, get_inbox_summary, filter_messages

def test_create():
    m = create_message(from_type="system", subject="Welcome!", body="Your account is ready")
    assert not m["read"]
    assert m["error"] is None

def test_invalid_type():
    m = create_message(from_type="spam", subject="X", body="Y")
    assert m["error"]

def test_summary():
    msgs = [{"read": False, "from_type": "system", "priority": "normal"},
            {"read": False, "from_type": "review", "priority": "urgent"},
            {"read": True, "from_type": "system", "priority": "normal"}]
    s = get_inbox_summary(messages=msgs)
    assert s["unread"] == 2
    assert s["urgent"] == 1

def test_filter():
    msgs = [{"from_type": "system", "read": False, "created_at": "2026-01-01"},
            {"from_type": "review", "read": True, "created_at": "2026-01-02"}]
    r = filter_messages(messages=msgs, unread_only=True)
    assert len(r) == 1
    assert r[0]["from_type"] == "system"
