from app.services.app_marketplace_extension_content_mod_queue import ContentModQueueService

def test_submit_normal():
    svc = ContentModQueueService()
    item = svc.submit("review", "Great extension!", "u1", "ext-1")
    assert item.status == "pending"

def test_auto_escalate():
    svc = ContentModQueueService()
    item = svc.submit("review", "This is a scam", "u1", "ext-1")
    assert item.status == "escalated"

def test_review_action():
    svc = ContentModQueueService()
    item = svc.submit("review", "Normal content", "u1", "ext-1")
    assert svc.review(item.item_id, "mod-1", "approved") is True
    assert item.status == "approved"
    assert len(svc.get_pending()) == 0

def test_stats():
    svc = ContentModQueueService()
    svc.submit("review", "A", "u1", "ext-1")
    svc.submit("review", "Spam link", "u2", "ext-1")
    stats = svc.get_stats()
    assert stats.get("pending", 0) == 1
    assert stats.get("escalated", 0) == 1
