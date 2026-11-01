from app.services.app_marketplace_extension_persistent_queue import PersistentQueueService
import time


def test_send_and_receive():
    q = PersistentQueueService()
    q.send({"task": "process"})
    results = q.receive()
    assert len(results) == 1
    assert results[0][1].body["task"] == "process"


def test_ack_removes():
    q = PersistentQueueService()
    q.send({"x": 1})
    [(receipt, msg)] = q.receive()
    assert q.ack(receipt) is True
    assert q.stats()["total"] == 0


def test_nack_returns():
    q = PersistentQueueService()
    q.send({"x": 1})
    [(receipt, _)] = q.receive(visibility_timeout=10)
    q.nack(receipt)
    # Should be receivable again
    results = q.receive()
    assert len(results) == 1


def test_visibility_timeout():
    q = PersistentQueueService(default_visibility_timeout=0.01)
    q.send({"x": 1})
    q.receive()  # now invisible
    # Immediately try again — should be empty
    assert len(q.receive()) == 0
    time.sleep(0.02)
    # Now visible again
    results = q.receive()
    assert len(results) == 1


def test_dead_letter():
    q = PersistentQueueService(default_visibility_timeout=0.001, max_receives=2)
    q.send({"poison": True})
    q.receive(); time.sleep(0.002)
    q.receive(); time.sleep(0.002)
    q.receive()  # third time → dead letter
    assert len(q.get_dead_letters()) == 1


def test_deduplication():
    q = PersistentQueueService()
    id1 = q.send({"x": 1}, dedup_id="dedup-1")
    id2 = q.send({"x": 2}, dedup_id="dedup-1")
    assert id1 != ""
    assert id2 == ""  # deduplicated
    assert q.stats()["total"] == 1


def test_batch_receive():
    q = PersistentQueueService()
    for i in range(5):
        q.send({"i": i})
    results = q.receive(max_messages=3)
    assert len(results) == 3


def test_fifo_ordering():
    q = PersistentQueueService()
    for i in range(5):
        q.send({"order": i})
    results = q.receive(max_messages=5)
    orders = [r[1].body["order"] for r in results]
    assert orders == [0, 1, 2, 3, 4]


def test_extend_visibility():
    q = PersistentQueueService(default_visibility_timeout=0.01)
    q.send({"x": 1})
    [(receipt, _)] = q.receive()
    q.extend_visibility(receipt, 10)
    time.sleep(0.02)
    # Should still be invisible (extended)
    assert len(q.receive()) == 0


def test_purge():
    q = PersistentQueueService()
    for i in range(10):
        q.send({"i": i})
    assert q.purge() == 10
    assert q.stats()["total"] == 0
