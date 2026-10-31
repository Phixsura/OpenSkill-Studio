from app.services.app_marketplace_notification_service import (
    NotificationService, NotificationChannel, NotificationPriority,
)


def test_send_and_inbox():
    ns = NotificationService()
    notif = ns.send("n1", "dev-1", "New install!", "Your extension was installed",
                     channel=NotificationChannel.IN_APP)
    assert notif is not None
    inbox = ns.get_inbox("dev-1")
    assert len(inbox) == 1
    assert inbox[0].title == "New install!"


def test_unread_count_and_mark_read():
    ns = NotificationService()
    ns.send("n10", "dev-2", "Review", "New review on your extension")
    ns.send("n11", "dev-2", "Install", "New install")
    assert ns.unread_count("dev-2") == 2
    ns.mark_read("n10")
    assert ns.unread_count("dev-2") == 1
    unread = ns.get_inbox("dev-2", unread_only=True)
    assert len(unread) == 1


def test_channel_preferences():
    ns = NotificationService()
    ns.set_preferences("dev-3", {"email": False, "in_app": True})
    email = ns.send("n20", "dev-3", "Email test", "body", channel=NotificationChannel.EMAIL)
    assert email is None  # email disabled
    in_app = ns.send("n21", "dev-3", "In-app test", "body", channel=NotificationChannel.IN_APP)
    assert in_app is not None


def test_broadcast():
    ns = NotificationService()
    sent = ns.broadcast(["u1", "u2", "u3"], "System Update", "Platform v2.0 released",
                         priority=NotificationPriority.HIGH)
    assert sent == 3
    assert ns.unread_count("u2") == 1


def test_priority():
    ns = NotificationService()
    ns.send("n30", "dev-4", "Alert!", "Security issue", priority=NotificationPriority.URGENT)
    inbox = ns.get_inbox("dev-4")
    assert inbox[0].priority == NotificationPriority.URGENT
