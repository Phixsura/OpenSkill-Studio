from app.services.app_marketplace_app_queue_manager import AppQueue

def test_enqueue_dequeue():
    q = AppQueue()
    q.enqueue({"type": "webhook", "data": "test"})
    msg = q.dequeue()
    assert msg["type"] == "webhook"

def test_empty():
    q = AppQueue()
    assert q.dequeue() is None

def test_peek():
    q = AppQueue()
    q.enqueue({"id": "1"})
    q.enqueue({"id": "2"})
    assert q.peek()["id"] == "1"
    assert q.stats()["size"] == 2

def test_stats():
    q = AppQueue(max_size=100)
    q.enqueue({"x": 1})
    q.dequeue()
    s = q.stats()
    assert s["processed"] == 1
    assert s["size"] == 0

def test_max_size():
    q = AppQueue(max_size=2)
    q.enqueue({"id": "1"})
    q.enqueue({"id": "2"})
    q.enqueue({"id": "3"})  # Oldest dropped
    assert q.stats()["size"] == 2
