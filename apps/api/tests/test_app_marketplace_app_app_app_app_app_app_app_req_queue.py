from app.services.app_marketplace_app_app_app_app_app_app_app_req_queue import RequestQueue

def test_enqueue_dequeue():
    q = RequestQueue()
    q.enqueue("r1", {"url": "/api"}, priority=1)
    q.enqueue("r2", {"url": "/api"}, priority=5)
    item = q.dequeue()
    assert item["id"] == "r2"  # higher priority
    q.ack(item)
    assert q.stats()["processed"] == 1

def test_dlq():
    q = RequestQueue(max_retries=2)
    q.enqueue("r1", {})
    item = q.dequeue()
    q.nack(item, "err1")
    item2 = q.dequeue()
    r = q.nack(item2, "err2")
    assert r["action"] == "dead_lettered"
    assert q.stats()["dlq_size"] == 1
