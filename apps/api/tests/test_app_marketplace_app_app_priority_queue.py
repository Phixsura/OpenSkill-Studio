from app.services.app_marketplace_app_app_priority_queue import MultiLevelQueue

def test_priority_order():
    q = MultiLevelQueue()
    q.enqueue(task={"name": "low"}, priority=3)
    q.enqueue(task={"name": "critical"}, priority=0)
    q.enqueue(task={"name": "medium"}, priority=2)
    t = q.dequeue()
    assert t["data"]["name"] == "critical"

def test_fifo_within_priority():
    q = MultiLevelQueue()
    q.enqueue(task={"n": "first"}, priority=1)
    q.enqueue(task={"n": "second"}, priority=1)
    assert q.dequeue()["data"]["n"] == "first"

def test_empty():
    q = MultiLevelQueue()
    assert q.dequeue() is None

def test_stats():
    q = MultiLevelQueue()
    q.enqueue(task={}, priority=0)
    q.enqueue(task={}, priority=2)
    q.enqueue(task={}, priority=2)
    s = q.stats()
    assert s["pending"] == 3
    assert s["has_critical"]
    assert s["by_priority"]["medium"] == 2
