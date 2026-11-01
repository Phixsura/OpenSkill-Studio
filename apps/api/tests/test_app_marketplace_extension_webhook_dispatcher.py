from app.services.app_marketplace_extension_webhook_dispatcher import WebhookDispatcherService


def test_fan_out():
    wd = WebhookDispatcherService()
    wd.subscribe("order.created", "sub-1", "https://a.com/hook", "secret-a")
    wd.subscribe("order.created", "sub-2", "https://b.com/hook", "secret-b")
    attempts = wd.dispatch("order.created", "evt-1", '{"order": 1}')
    assert len(attempts) == 2
    assert all(a.status == "delivered" for a in attempts)


def test_signature():
    wd = WebhookDispatcherService()
    sig = wd.sign_payload('{"test": true}', "my-secret")
    assert len(sig) == 64  # SHA-256 hex


def test_circuit_breaker():
    wd = WebhookDispatcherService()
    wd.subscribe("event", "sub-1", "https://fail.com", "secret", max_failures=3)

    def failing(url, payload, sig):
        raise RuntimeError("down")

    for i in range(3):
        wd.dispatch("event", f"e{i}", "data", executor=failing)

    # Circuit should be open now
    attempts = wd.dispatch("event", "e99", "data", executor=failing)
    assert attempts[0].status == "circuit_open"


def test_successful_delivery_resets_failures():
    wd = WebhookDispatcherService()
    wd.subscribe("event", "sub-1", "https://api.com", "secret", max_failures=5)

    def failing(url, payload, sig):
        raise RuntimeError("err")

    wd.dispatch("event", "e1", "data", executor=failing)
    wd.dispatch("event", "e2", "data", executor=failing)
    # Now succeed
    wd.dispatch("event", "e3", "data")  # no executor = success
    sub = wd._subscribers["event"][0]
    assert sub.failure_count == 0


def test_retry_queue():
    wd = WebhookDispatcherService()
    wd.subscribe("event", "sub-1", "https://api.com", "secret")

    def failing(url, payload, sig):
        raise RuntimeError("timeout")

    wd.dispatch("event", "e1", "data", executor=failing)
    stats = wd.get_delivery_stats()
    assert stats["retry_queue"] >= 1


def test_no_subscribers():
    wd = WebhookDispatcherService()
    attempts = wd.dispatch("unknown.event", "e1", "data")
    assert len(attempts) == 0


def test_inactive_subscriber_skipped():
    wd = WebhookDispatcherService()
    sub = wd.subscribe("event", "sub-1", "https://api.com", "secret")
    sub.active = False
    attempts = wd.dispatch("event", "e1", "data")
    assert len(attempts) == 0


def test_subscriber_health():
    wd = WebhookDispatcherService()
    wd.subscribe("event", "sub-1", "https://a.com", "s")
    wd.dispatch("event", "e1", "data")
    health = wd.get_subscriber_health("event")
    assert health[0]["success"] == 1
