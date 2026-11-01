from app.services.app_marketplace_delivery_queue import DeliveryQueue, DeliveryItem


def test_enqueue_dequeue():
    dq = DeliveryQueue()
    dq.enqueue(DeliveryItem("d1", "key1", "https://a.com", {"event": "test"}))
    items = dq.dequeue(1)
    assert len(items) == 1
    assert items[0].delivery_id == "d1"
    assert items[0].attempts == 1


def test_deduplication():
    dq = DeliveryQueue()
    dq.enqueue(DeliveryItem("d1", "key1", "https://a.com", {}))
    ok, msg = dq.enqueue(DeliveryItem("d2", "key1", "https://a.com", {}))
    assert ok is False
    assert "Duplicate" in msg


def test_acknowledge():
    dq = DeliveryQueue()
    dq.enqueue(DeliveryItem("d1", "k1", "url", {}))
    dq.dequeue()
    assert dq.acknowledge("d1") is True
    stats = dq.get_stats()
    assert stats["acknowledged"] == 1


def test_nack_requeue():
    dq = DeliveryQueue(max_attempts=3)
    dq.enqueue(DeliveryItem("d1", "k1", "url", {}))
    dq.dequeue()
    dq.nack("d1", "timeout")
    # Should be requeued
    items = dq.dequeue()
    assert len(items) == 1
    assert items[0].attempts == 2


def test_dead_letter():
    dq = DeliveryQueue(max_attempts=2)
    dq.enqueue(DeliveryItem("d1", "k1", "url", {}))
    dq.dequeue()  # attempt 1
    dq.nack("d1")
    dq.dequeue()  # attempt 2
    dq.nack("d1")
    dead = dq.get_dead_letter()
    assert len(dead) == 1


def test_peek():
    dq = DeliveryQueue()
    dq.enqueue(DeliveryItem("d1", "k1", "url", {}))
    dq.enqueue(DeliveryItem("d2", "k2", "url", {}))
    peeked = dq.peek(2)
    assert len(peeked) == 2
    # Peek should not consume
    assert dq.get_stats()["queue_size"] == 2


def test_queue_full():
    dq = DeliveryQueue(max_size=2)
    dq.enqueue(DeliveryItem("d1", "k1", "url", {}))
    dq.enqueue(DeliveryItem("d2", "k2", "url", {}))
    ok, msg = dq.enqueue(DeliveryItem("d3", "k3", "url", {}))
    assert ok is False
    assert "full" in msg
