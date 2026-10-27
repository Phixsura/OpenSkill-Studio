from app.services.app_marketplace_extension_pubsub_broker import PubSubBrokerService


def test_publish_and_poll():
    broker = PubSubBrokerService()
    broker.create_topic("events")
    broker.subscribe("group-1", "events")
    broker.publish("events", "user-1", {"action": "login"})
    broker.publish("events", "user-2", {"action": "signup"})
    msgs = broker.poll("group-1", "events")
    assert len(msgs) == 2
    assert msgs[0].value["action"] == "login"


def test_ack_advances_offset():
    broker = PubSubBrokerService()
    broker.subscribe("g1", "t1")
    m1 = broker.publish("t1", "k", {"n": 1})
    m2 = broker.publish("t1", "k", {"n": 2})
    msgs = broker.poll("g1", "t1")
    broker.ack("g1", "t1", m1.msg_id)
    broker.ack("g1", "t1", m2.msg_id)
    assert broker.get_lag("g1", "t1") == 0


def test_consumer_group_isolation():
    broker = PubSubBrokerService()
    broker.subscribe("g1", "topic")
    broker.subscribe("g2", "topic")
    broker.publish("topic", "k", {"data": 1})
    # Both groups see the same message independently
    msgs_g1 = broker.poll("g1", "topic")
    msgs_g2 = broker.poll("g2", "topic")
    assert len(msgs_g1) == 1
    assert len(msgs_g2) == 1


def test_lag_tracking():
    broker = PubSubBrokerService()
    broker.subscribe("g1", "t1")
    for i in range(10):
        broker.publish("t1", "k", {"i": i})
    assert broker.get_lag("g1", "t1") == 10
    msgs = broker.poll("g1", "t1", max_messages=3)
    for m in msgs:
        broker.ack("g1", "t1", m.msg_id)
    assert broker.get_lag("g1", "t1") == 7


def test_nack_dead_letter():
    broker = PubSubBrokerService()
    broker._max_redeliveries = 2
    broker.subscribe("g1", "t1")
    msg = broker.publish("t1", "k", {"poison": True})
    broker.poll("g1", "t1")
    broker.nack("g1", "t1", msg.msg_id)
    broker.nack("g1", "t1", msg.msg_id)  # exceeds max
    assert len(broker.get_dead_letters()) == 1


def test_max_messages():
    broker = PubSubBrokerService()
    broker.subscribe("g1", "t1")
    for i in range(20):
        broker.publish("t1", "k", {"i": i})
    msgs = broker.poll("g1", "t1", max_messages=5)
    assert len(msgs) == 5


def test_auto_create_topic():
    broker = PubSubBrokerService()
    msg = broker.publish("new-topic", "k", {"auto": True})
    assert msg.topic == "new-topic"


def test_stats():
    broker = PubSubBrokerService()
    broker.publish("t1", "k", {})
    broker.publish("t2", "k", {})
    broker.subscribe("g1", "t1")
    stats = broker.stats()
    assert stats["topics"] == 2
    assert stats["total_messages"] == 2
    assert stats["consumer_groups"] == 1
