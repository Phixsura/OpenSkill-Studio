from app.services.app_marketplace_extension_webhook_log import (
    WebhookLogService, WebhookDirection, LogStatus,
)


def test_log_and_search():
    svc = WebhookLogService()
    svc.log("ext-1", WebhookDirection.OUTBOUND, "deploy", "https://hooks.example.com",
            LogStatus.SUCCESS, status_code=200, latency_ms=45.2)
    results = svc.search("ext-1")
    assert len(results) == 1
    assert results[0].latency_ms == 45.2


def test_filter_by_status():
    svc = WebhookLogService()
    svc.log("ext-1", WebhookDirection.OUTBOUND, "deploy", "https://a.com", LogStatus.SUCCESS)
    svc.log("ext-1", WebhookDirection.OUTBOUND, "error", "https://a.com", LogStatus.FAILED)
    results = svc.search("ext-1", status=LogStatus.FAILED)
    assert len(results) == 1


def test_filter_by_direction():
    svc = WebhookLogService()
    svc.log("ext-1", WebhookDirection.INBOUND, "push", "https://a.com", LogStatus.SUCCESS)
    svc.log("ext-1", WebhookDirection.OUTBOUND, "notify", "https://a.com", LogStatus.SUCCESS)
    results = svc.search("ext-1", direction=WebhookDirection.INBOUND)
    assert len(results) == 1


def test_stats():
    svc = WebhookLogService()
    for _ in range(8):
        svc.log("ext-1", WebhookDirection.OUTBOUND, "e", "u", LogStatus.SUCCESS, latency_ms=10)
    for _ in range(2):
        svc.log("ext-1", WebhookDirection.OUTBOUND, "e", "u", LogStatus.FAILED, latency_ms=100)
    stats = svc.get_stats("ext-1")
    assert stats["total"] == 10
    assert stats["success_rate"] == 80.0


def test_error_summary():
    svc = WebhookLogService()
    svc.log("ext-1", WebhookDirection.OUTBOUND, "e", "u", LogStatus.FAILED, error_message="timeout")
    svc.log("ext-1", WebhookDirection.OUTBOUND, "e", "u", LogStatus.FAILED, error_message="timeout")
    svc.log("ext-1", WebhookDirection.OUTBOUND, "e", "u", LogStatus.TIMEOUT, error_message="connection refused")
    summary = svc.get_error_summary("ext-1")
    assert summary[0]["error"] == "timeout"
    assert summary[0]["count"] == 2


def test_purge():
    svc = WebhookLogService()
    svc.log("ext-1", WebhookDirection.OUTBOUND, "e", "u", LogStatus.SUCCESS)
    svc.log("ext-2", WebhookDirection.OUTBOUND, "e", "u", LogStatus.SUCCESS)
    purged = svc.purge("ext-1")
    assert purged == 1
    assert len(svc.search("ext-2")) == 1
