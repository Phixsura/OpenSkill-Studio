from app.services.app_marketplace_complete_app_review_page import build_complete_review_page_v2

def test_page():
    reviews = [{"rating": 5, "helpful_yes": 10}, {"rating": 3, "helpful_yes": 50}, {"rating": 4, "helpful_yes": 5}]
    p = build_complete_review_page_v2(
        app={"id": "a1", "name": "App"}, reviews=reviews,
        stats={"avg_rating": 4.0, "count": 3}, developer_reply_rate=66.7, sort_by="helpful")
    assert p["reviews"][0]["helpful_yes"] == 50  # most helpful first
    assert p["developer_reply_rate"] == 66.7
    assert len(p["sort_options"]) == 4
