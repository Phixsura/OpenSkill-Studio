from app.services.app_marketplace_app_app_app_app_app_app_app_priority_router import PriorityRouter

def test_priority_order():
    pr = PriorityRouter()
    pr.enqueue("r1", "low")
    pr.enqueue("r2", "critical")
    pr.enqueue("r3", "normal")
    item = pr.dequeue()
    assert item["id"] == "r2"  # critical first
    item2 = pr.dequeue()
    assert item2["id"] == "r3"  # normal before low

def test_stats():
    pr = PriorityRouter()
    pr.enqueue("a", "high")
    pr.enqueue("b", "low")
    pr.dequeue()
    s = pr.stats()
    assert s["total_queued"] == 1
    assert s["processed"] == 1
