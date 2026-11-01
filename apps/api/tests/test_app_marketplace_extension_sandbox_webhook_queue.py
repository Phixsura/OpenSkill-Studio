from app.services.app_marketplace_extension_sandbox_webhook_queue import (
    SandboxWebhookQueueService, WebhookPriority, DeliveryState,
)


def test_enqueue_and_dequeue():
    svc = SandboxWebhookQueueService()
    svc.enqueue("sb-1", "https://a.com/hook", '{"event":"deploy"}')
    wh = svc.dequeue("sb-1")
    assert wh is not None
    assert wh.state == DeliveryState.DELIVERING


def test_priority_ordering():
    svc = SandboxWebhookQueueService()
    svc.enqueue("sb-1", "https://a.com", '{}', WebhookPriority.LOW)
    svc.enqueue("sb-1", "https://b.com", '{}', WebhookPriority.CRITICAL)
    wh = svc.dequeue("sb-1")
    assert wh.url == "https://b.com"


def test_confirm_delivery():
    svc = SandboxWebhookQueueService()
    wh = svc.enqueue("sb-1", "https://a.com", '{}')
    svc.dequeue("sb-1")
    assert svc.confirm(wh.webhook_id, "sb-1") is True
    assert wh.state == DeliveryState.DELIVERED


def test_fail_and_retry():
    svc = SandboxWebhookQueueService()
    wh = svc.enqueue("sb-1", "https://a.com", '{}', max_attempts=3)
    svc.dequeue("sb-1")
    state = svc.fail(wh.webhook_id, "sb-1")
    assert state == DeliveryState.RETRY


def test_fail_exhausted():
    svc = SandboxWebhookQueueService()
    wh = svc.enqueue("sb-1", "https://a.com", '{}', max_attempts=1)
    svc.dequeue("sb-1")
    state = svc.fail(wh.webhook_id, "sb-1")
    assert state == DeliveryState.FAILED


def test_payload_too_large():
    svc = SandboxWebhookQueueService()
    result = svc.enqueue("sb-1", "https://a.com", "x" * (1024 * 1024 + 1))
    assert isinstance(result, dict) and "error" in result


def test_queue_depth():
    svc = SandboxWebhookQueueService()
    svc.enqueue("sb-1", "https://a.com", '{}')
    svc.enqueue("sb-1", "https://b.com", '{}')
    depth = svc.get_depth("sb-1")
    assert depth["pending"] == 2
    assert depth["total"] == 2


def test_by_priority():
    svc = SandboxWebhookQueueService()
    svc.enqueue("sb-1", "https://a.com", '{}', WebhookPriority.HIGH)
    svc.enqueue("sb-1", "https://b.com", '{}', WebhookPriority.HIGH)
    svc.enqueue("sb-1", "https://c.com", '{}', WebhookPriority.LOW)
    by_pri = svc.get_by_priority("sb-1")
    assert by_pri["high"] == 2
    assert by_pri["low"] == 1
