from app.services.app_marketplace_app_smart_notifications import should_notify_immediately, batch_notifications, compute_notification_digest

def test_immediate_security():
    assert should_notify_immediately(event_type="security_alert", severity="high")

def test_immediate_critical():
    assert should_notify_immediately(event_type="anything", severity="critical")

def test_not_immediate():
    assert not should_notify_immediately(event_type="new_review", severity="low")

def test_batch():
    notifs = [{"category": "reviews"}, {"category": "reviews"}, {"category": "installs"}]
    b = batch_notifications(notifications=notifs)
    assert len(b) == 2  # 1 batch for reviews + 1 single install

def test_digest():
    notifs = [{"type": "info"}, {"type": "warning", "severity": "critical"}, {"type": "info"}]
    d = compute_notification_digest(notifications=notifs)
    assert d["total"] == 3
    assert d["has_urgent"]
