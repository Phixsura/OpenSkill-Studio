from app.services.app_developer_notification_digest import build_digest

EVENTS = [{"type": "app_installed"}, {"type": "app_installed"}, {"type": "review_decided"}, {"type": "error"}]

def test_digest():
    d = build_digest(EVENTS)
    assert d["total_events"] == 4
    assert len(d["highlights"]) == 3

def test_empty():
    d = build_digest([])
    assert d["total_events"] == 0

def test_period():
    d = build_digest(EVENTS, period="weekly")
    assert d["period"] == "weekly"
