from app.services.app_marketplace_extension_priority_queue import PriorityQueueService
import time


def test_basic_priority_order():
    q = PriorityQueueService(aging_rate=0)
    q.enqueue("low-task", {}, "low")
    q.enqueue("critical-task", {}, "critical")
    q.enqueue("normal-task", {}, "normal")
    item = q.dequeue()
    assert item.item_id == "critical-task"


def test_same_priority_fifo():
    q = PriorityQueueService(aging_rate=0)
    q.enqueue("first", {}, "normal")
    q.enqueue("second", {}, "normal")
    q.enqueue("third", {}, "normal")
    assert q.dequeue().item_id == "first"
    assert q.dequeue().item_id == "second"


def test_aging_prevents_starvation():
    q = PriorityQueueService(aging_rate=100)  # fast aging for test
    q.enqueue("low-old", {"desc": "old low priority"}, "low")
    # Backdate the item to simulate waiting
    q._heap[0].enqueued_at = time.time() - 10
    q.enqueue("high-new", {"desc": "new high priority"}, "high")
    # After aging, the old low-priority item should have aged to ~0 priority
    item = q.dequeue()
    assert item.item_id == "low-old"  # aged past high priority


def test_peek():
    q = PriorityQueueService(aging_rate=0)
    q.enqueue("a", {}, "critical")
    peeked = q.peek()
    assert peeked.item_id == "a"
    assert q.size() == 1  # not removed


def test_batch_dequeue():
    q = PriorityQueueService(aging_rate=0)
    for i in range(5):
        q.enqueue(f"task-{i}", {}, "normal")
    items = q.dequeue_batch(3)
    assert len(items) == 3
    assert q.size() == 2


def test_empty_dequeue():
    q = PriorityQueueService(aging_rate=0)
    assert q.dequeue() is None
    assert q.peek() is None
    assert q.dequeue_batch(5) == []


def test_integer_priority():
    q = PriorityQueueService(aging_rate=0)
    q.enqueue("p0", {}, 0)
    q.enqueue("p3", {}, 3)
    assert q.dequeue().item_id == "p0"


def test_stats():
    q = PriorityQueueService(aging_rate=0)
    q.enqueue("a", {}, "critical")
    q.enqueue("b", {}, "normal")
    q.enqueue("c", {}, "low")
    q.dequeue()
    stats = q.stats()
    assert stats["size"] == 2
    assert stats["total_enqueued"] == 3
    assert stats["total_dequeued"] == 1
    assert stats["by_priority"]["critical"] == 0  # dequeued
    assert stats["by_priority"]["normal"] == 1
