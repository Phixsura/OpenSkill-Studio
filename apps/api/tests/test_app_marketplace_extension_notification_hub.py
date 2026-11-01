from app.services.app_marketplace_extension_notification_hub import (
    NotificationHubService, Channel,
)


def test_send_notification():
    svc = NotificationHubService()
    svc.register_template("deploy", "Deploy: {{version}}", "Deployed {{ext}} {{version}}")
    n = svc.send("deploy", "user-1", {"version": "2.0", "ext": "Slack Bot"})
    assert n is not None
    assert n.title == "Deploy: 2.0"
    assert "Slack Bot" in n.body


def test_user_preferences():
    svc = NotificationHubService()
    svc.register_template("alert", "Alert", "Something happened")
    svc.set_preferences("user-1", "alert", [Channel.EMAIL, Channel.PUSH])
    n = svc.send("alert", "user-1", {})
    assert "email" in n.channels
    assert "push" in n.channels


def test_dedup():
    svc = NotificationHubService()
    svc.register_template("deploy", "Deploy", "Deployed")
    n1 = svc.send("deploy", "user-1", {}, dedup_key="deploy-v2")
    n2 = svc.send("deploy", "user-1", {}, dedup_key="deploy-v2")
    assert n1 is not None
    assert n2 is None


def test_inbox():
    svc = NotificationHubService()
    svc.register_template("event", "Event", "msg")
    svc.send("event", "user-1", {})
    svc.send("event", "user-1", {})
    svc.send("event", "user-2", {})
    assert len(svc.get_inbox("user-1")) == 2


def test_mark_read():
    svc = NotificationHubService()
    svc.register_template("event", "E", "M")
    n = svc.send("event", "user-1", {})
    svc.mark_read(n.notification_id)
    assert svc.get_unread_count("user-1") == 0
