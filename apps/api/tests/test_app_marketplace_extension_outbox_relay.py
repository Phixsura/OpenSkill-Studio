from app.services.app_marketplace_extension_outbox_relay import OutboxRelayService


def test_enqueue_and_poll():
    relay = OutboxRelayService()
    relay.enqueue("m1", "user-1", "events", {"action": "login"})
    relay.enqueue("m2", "user-2", "events", {"action": "signup"})
    batch = relay.poll(10)
    assert len(batch) == 2


def test_deliver():
    relay = OutboxRelayService()
    relay.enqueue("m1", "key", "topic", {"data": 1})
    result = relay.deliver("m1")
    assert result["status"] == "delivered"
    # Subsequent poll excludes delivered
    assert len(relay.poll()) == 0


def test_relay_batch():
    relay = OutboxRelayService()
    for i in range(5):
        relay.enqueue(f"m{i}", "key", "topic", {"i": i})
    result = relay.relay_batch(batch_size=5)
    assert result["delivered"] == 5


def test_publisher_failure():
    relay = OutboxRelayService()
    relay.enqueue("m1", "key", "topic", {})
    def failing_pub(topic, key, payload):
        raise RuntimeError("broker down")
    result = relay.deliver("m1", publisher=failing_pub)
    assert result["status"] == "failed"


def test_poison_after_max_attempts():
    relay = OutboxRelayService()
    msg = relay.enqueue("m1", "key", "topic", {})
    msg.max_attempts = 2
    def fail(t, k, p): raise RuntimeError("err")
    relay.deliver("m1", fail)  # attempt 1
    relay.deliver("m1", fail)  # attempt 2 → poison
    assert len(relay.get_poison_messages()) == 1


def test_retry_poison():
    relay = OutboxRelayService()
    msg = relay.enqueue("m1", "key", "topic", {})
    msg.max_attempts = 1
    def fail(t, k, p): raise RuntimeError("err")
    relay.deliver("m1", fail)  # → poison
    relay.retry_poison("m1")
    result = relay.deliver("m1")  # retry succeeds (no publisher = success)
    assert result["status"] == "delivered"


def test_consumer_dedup():
    relay = OutboxRelayService()
    assert relay.is_duplicate("m1") is False
    assert relay.is_duplicate("m1") is True


def test_ordering_by_partition():
    relay = OutboxRelayService()
    relay.enqueue("m2", "b", "t", {})
    relay.enqueue("m1", "a", "t", {})
    relay.enqueue("m3", "a", "t", {})
    batch = relay.poll()
    keys = [m.partition_key for m in batch]
    # 'a' messages should be together and in order
    a_msgs = [m for m in batch if m.partition_key == "a"]
    assert a_msgs[0].message_id == "m1"


def test_metrics():
    relay = OutboxRelayService()
    relay.enqueue("m1", "k", "t", {})
    relay.relay_batch()
    metrics = relay.get_metrics()
    assert metrics["total_delivered"] == 1
    assert metrics["pending"] == 0
