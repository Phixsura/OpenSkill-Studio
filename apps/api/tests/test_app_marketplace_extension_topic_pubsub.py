from app.services.app_marketplace_extension_topic_pubsub import TopicPubSubService


def test_exact_match():
    ps = TopicPubSubService()
    ps.subscribe("events.user.login", "s1")
    result = ps.publish("events.user.login", {"user": "alice"})
    assert "s1" in result["delivered_to"]


def test_no_match():
    ps = TopicPubSubService()
    ps.subscribe("events.user.login", "s1")
    result = ps.publish("events.order.created", {})
    assert result["count"] == 0


def test_single_wildcard():
    ps = TopicPubSubService()
    ps.subscribe("events.user.+", "s1")
    r1 = ps.publish("events.user.login", {})
    r2 = ps.publish("events.user.logout", {})
    r3 = ps.publish("events.order.created", {})
    assert r1["count"] == 1
    assert r2["count"] == 1
    assert r3["count"] == 0


def test_multi_wildcard():
    ps = TopicPubSubService()
    ps.subscribe("events.#", "s1")
    r1 = ps.publish("events.user.login", {})
    r2 = ps.publish("events.order.created.confirmed", {})
    assert r1["count"] == 1
    assert r2["count"] == 1


def test_broadcast():
    ps = TopicPubSubService()
    ps.subscribe("topic", "s1")
    ps.subscribe("topic", "s2")
    ps.subscribe("topic", "s3")
    result = ps.publish("topic", {})
    assert result["count"] == 3


def test_competing_consumers():
    ps = TopicPubSubService()
    ps.subscribe("tasks", "w1", group="workers")
    ps.subscribe("tasks", "w2", group="workers")
    ps.subscribe("tasks", "w3", group="workers")
    # Each message goes to ONE worker in round-robin
    results = [ps.publish("tasks", {"i": i}) for i in range(3)]
    delivered = [r["delivered_to"][0] for r in results]
    assert set(delivered) == {"w1", "w2", "w3"}


def test_mixed_broadcast_and_group():
    ps = TopicPubSubService()
    ps.subscribe("events", "logger")  # broadcast
    ps.subscribe("events", "worker-1", group="workers")
    ps.subscribe("events", "worker-2", group="workers")
    result = ps.publish("events", {})
    # logger gets it + one worker gets it
    assert result["count"] == 2
    assert "logger" in result["delivered_to"]


def test_unsubscribe():
    ps = TopicPubSubService()
    ps.subscribe("topic", "s1")
    ps.unsubscribe("s1")
    result = ps.publish("topic", {})
    assert result["count"] == 0


def test_get_messages():
    ps = TopicPubSubService()
    ps.subscribe("events.#", "collector")
    ps.publish("events.a", {"val": 1})
    ps.publish("events.b", {"val": 2})
    msgs = ps.get_messages("collector")
    assert len(msgs) == 2


def test_hash_at_end():
    ps = TopicPubSubService()
    ps.subscribe("logs.#", "s1")
    assert ps.publish("logs", {})["count"] == 1
    assert ps.publish("logs.error", {})["count"] == 1
    assert ps.publish("logs.error.critical", {})["count"] == 1
