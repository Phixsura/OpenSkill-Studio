from app.services.app_marketplace_app_app_app_app_app_app_app_msg_broker import MessageBroker

def test_pubsub():
    mb = MessageBroker()
    mb.create_topic("orders")
    mb.subscribe("orders", "email-svc")
    mb.subscribe("orders", "analytics-svc")
    r = mb.publish("orders", {"type": "order.created", "id": "o1"})
    assert r["delivered_to"] == 2
    msgs = mb.consume("email-svc")
    assert len(msgs) == 1
    assert msgs[0]["type"] == "order.created"
    assert mb.stats()["pending"] == 1  # analytics still pending
