from app.services.app_marketplace_extension_sandbox_notification_queue import (
    SandboxNotificationQueueService, NotificationPriority,
)


def test_send_and_get_unread():
    svc = SandboxNotificationQueueService()
    svc.send("sb-1", "Deploy Complete", "v1.0 deployed", NotificationPriority.HIGH)
    svc.send("sb-1", "Info", "FYI update", NotificationPriority.LOW)
    unread = svc.get_unread("sb-1")
    assert len(unread) == 2
    assert unread[0].priority == NotificationPriority.HIGH  # sorted by priority


def test_mark_read():
    svc = SandboxNotificationQueueService()
    n = svc.send("sb-1", "Test", "msg")
    svc.mark_read("sb-1", n.notification_id)
    assert len(svc.get_unread("sb-1")) == 0


def test_mark_all_read():
    svc = SandboxNotificationQueueService()
    svc.send("sb-1", "A", "1")
    svc.send("sb-1", "B", "2")
    svc.send("sb-1", "C", "3")
    count = svc.mark_all_read("sb-1")
    assert count == 3
    assert len(svc.get_unread("sb-1")) == 0


def test_deduplication():
    svc = SandboxNotificationQueueService()
    n1 = svc.send("sb-1", "Alert", "msg", dedup_key="deploy-123")
    n2 = svc.send("sb-1", "Alert", "msg", dedup_key="deploy-123")
    assert n1 is not None
    assert n2 is None  # suppressed


def test_category_filter():
    svc = SandboxNotificationQueueService()
    svc.send("sb-1", "Deploy", "done", category="deploy")
    svc.send("sb-1", "Error", "crash", category="error")
    svc.send("sb-1", "Deploy2", "done2", category="deploy")
    deploys = svc.get_by_category("sb-1", "deploy")
    assert len(deploys) == 2


def test_unread_count():
    svc = SandboxNotificationQueueService()
    svc.send("sb-1", "A", "m", NotificationPriority.HIGH)
    svc.send("sb-1", "B", "m", NotificationPriority.HIGH)
    svc.send("sb-1", "C", "m", NotificationPriority.LOW)
    counts = svc.get_unread_count("sb-1")
    assert counts["total"] == 3
    assert counts["by_priority"]["high"] == 2


def test_delete():
    svc = SandboxNotificationQueueService()
    n = svc.send("sb-1", "Temp", "msg")
    assert svc.delete("sb-1", n.notification_id) is True
    assert len(svc.get_unread("sb-1")) == 0


def test_clear():
    svc = SandboxNotificationQueueService()
    svc.send("sb-1", "A", "1")
    svc.send("sb-1", "B", "2")
    assert svc.clear("sb-1") == 2
