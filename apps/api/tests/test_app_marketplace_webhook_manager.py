from app.services.app_marketplace_webhook_manager import (
    create_subscription, get_subscription, list_subscriptions,
    deactivate_subscription, sign_payload, verify_signature,
    dispatch_event, get_delivery_log,
)


def test_create_and_get():
    sub = create_subscription("wh-001", "https://example.com/hook",
                               ["submission.created"], "alice", secret="s3cret")
    assert sub["sub_id"] == "wh-001"
    assert sub["active"] is True
    fetched = get_subscription("wh-001")
    assert fetched is not None


def test_list_by_owner_and_event():
    create_subscription("wh-010", "https://a.com", ["build.success"], "bob")
    create_subscription("wh-011", "https://b.com", ["build.success", "deploy.done"], "carol")
    by_bob = list_subscriptions(owner="bob")
    assert all(s["owner"] == "bob" for s in by_bob)
    by_event = list_subscriptions(event="deploy.done")
    assert all("deploy.done" in s["events"] for s in by_event)


def test_deactivate():
    create_subscription("wh-020", "https://x.com", ["test.pass"], "dave")
    assert deactivate_subscription("wh-020") is True
    active = list_subscriptions(owner="dave")
    assert all(s["sub_id"] != "wh-020" for s in active)


def test_sign_and_verify():
    sig = sign_payload('{"event":"test"}', "my_secret")
    assert verify_signature('{"event":"test"}', "my_secret", sig) is True
    assert verify_signature('{"event":"test"}', "wrong", sig) is False


def test_dispatch_and_log():
    create_subscription("wh-030", "https://hooks.test/a", ["review.created"], "eve")
    deliveries = dispatch_event("review.created", {"review_id": "r1"})
    assert len(deliveries) >= 1
    assert deliveries[0]["status"] == "delivered"
    log = get_delivery_log("wh-030")
    assert len(log) >= 1
