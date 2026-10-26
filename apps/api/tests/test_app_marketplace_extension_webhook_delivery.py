from app.services.app_marketplace_extension_webhook_delivery import (
    WebhookDeliveryService, DeliveryState, CircuitState,
)


def test_enqueue_delivery():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com/events")
    d = svc.enqueue("ep-1", '{"event": "deploy"}')
    assert d is not None
    assert d.state == DeliveryState.QUEUED


def test_successful_delivery():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com")
    d = svc.enqueue("ep-1", "{}")
    svc.process_result(d.delivery_id, success=True, status_code=200)
    assert d.state == DeliveryState.DELIVERED


def test_retry_on_failure():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com")
    d = svc.enqueue("ep-1", "{}", max_retries=3)
    svc.process_result(d.delivery_id, success=False, status_code=500, error="timeout")
    assert d.state == DeliveryState.RETRYING
    assert d.attempts == 1


def test_dead_letter_after_max_retries():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com")
    d = svc.enqueue("ep-1", "{}", max_retries=2)
    svc.process_result(d.delivery_id, False, 500)
    svc.process_result(d.delivery_id, False, 500)
    assert d.state == DeliveryState.DEAD_LETTER
    assert len(svc.get_dead_letters()) == 1


def test_circuit_breaker():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com", failure_threshold=3)
    for _ in range(3):
        d = svc.enqueue("ep-1", "{}", max_retries=1)
        svc.process_result(d.delivery_id, False, 500)
    ep = svc._endpoints["ep-1"]
    assert ep.circuit_state == CircuitState.OPEN
    # Cannot enqueue while open
    assert svc.enqueue("ep-1", "{}") is None


def test_reset_circuit():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com", failure_threshold=1)
    d = svc.enqueue("ep-1", "{}", max_retries=1)
    svc.process_result(d.delivery_id, False, 500)
    assert svc.reset_circuit("ep-1") is True
    assert svc._endpoints["ep-1"].circuit_state == CircuitState.HALF_OPEN


def test_queue_stats():
    svc = WebhookDeliveryService()
    svc.register_endpoint("ep-1", "https://hooks.example.com")
    svc.enqueue("ep-1", "{}")
    svc.enqueue("ep-1", "{}")
    stats = svc.get_queue_stats()
    assert stats["total"] == 2
    assert stats["by_state"]["queued"] == 2
