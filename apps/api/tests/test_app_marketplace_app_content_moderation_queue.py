from app.services.app_marketplace_app_content_moderation_queue import add_to_queue, process_item, get_queue_stats

def test_add():
    r = add_to_queue(content_type="review", content_id="r1", reason="Spam", reported_by="u1")
    assert r["queue_id"].startswith("mod_")
    assert r["status"] == "pending"

def test_invalid_type():
    r = add_to_queue(content_type="meme", content_id="x", reason="x", reported_by="u1")
    assert "error" in r

def test_process():
    r = process_item(queue_id="mod_1", action="reject", moderator="admin", note="Confirmed spam")
    assert r["action"] == "reject"

def test_stats():
    items = [{"status": "pending", "content_type": "review"},
             {"status": "processed", "content_type": "review"},
             {"status": "pending", "content_type": "comment"}]
    r = get_queue_stats(items=items)
    assert r["pending"] == 2
    assert r["by_type"]["review"] == 2
