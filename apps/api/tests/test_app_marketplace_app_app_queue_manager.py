from app.services.app_marketplace_app_app_queue_manager import TaskQueue

def test_push_pop():
    q = TaskQueue()
    q.push(task={"name": "build"}, priority=1)
    q.push(task={"name": "deploy"}, priority=10)
    t = q.pop()
    assert t["data"]["name"] == "deploy"  # higher priority first

def test_fifo_same_priority():
    q = TaskQueue()
    q.push(task={"name": "first"})
    q.push(task={"name": "second"})
    assert q.pop()["data"]["name"] == "first"

def test_empty_pop():
    q = TaskQueue()
    assert q.pop() is None

def test_full():
    q = TaskQueue(max_size=2)
    q.push(task={"a": 1})
    q.push(task={"b": 2})
    r = q.push(task={"c": 3})
    assert "error" in r

def test_stats():
    q = TaskQueue(max_size=10)
    q.push(task={"x": 1})
    q.pop()
    s = q.stats()
    assert s["processed"] == 1
    assert s["pending"] == 0
