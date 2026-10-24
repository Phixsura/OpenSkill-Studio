from app.services.app_marketplace_app_app_app_app_app_app_app_content_moderation import moderate_content

def test_moderation():
    items = [
        {"id": "c1", "text": "Great app!", "reported_count": 0},
        {"id": "c2", "text": "This is spam buy now", "reported_count": 0},
        {"id": "c3", "text": "Decent tool", "reported_count": 5},
    ]
    r = moderate_content(items)
    assert r["total"] == 3
    assert r["counts"]["approved"] == 1
    assert r["counts"]["rejected"] == 1
    assert r["counts"]["flagged"] == 1
    assert r["results"][0]["status"] == "approved"
    assert r["results"][1]["status"] == "rejected"
    assert "blocked_word" in r["results"][1]["flags"]
    assert r["results"][2]["status"] == "flagged"
    assert r["queue_health"] == "needs_review"
