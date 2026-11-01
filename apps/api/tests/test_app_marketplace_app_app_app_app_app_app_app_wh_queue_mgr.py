from app.services.app_marketplace_app_app_app_app_app_app_app_wh_queue_mgr import WebhookQueueManager

def test_enqueue_dequeue():
    wqm = WebhookQueueManager()
    wqm.enqueue("sub-1", {"type": "order.created"})
    wqm.enqueue("sub-1", {"type": "order.paid"})
    r = wqm.dequeue("sub-1", batch_size=1)
    assert r["count"] == 1
    assert r["remaining"] == 1
    assert wqm.stats()["processed"] == 1

def test_full():
    wqm = WebhookQueueManager(max_queue_size=2)
    wqm.enqueue("sub-1", {"a": 1})
    wqm.enqueue("sub-1", {"a": 2})
    r = wqm.enqueue("sub-1", {"a": 3})
    assert not r["enqueued"]
