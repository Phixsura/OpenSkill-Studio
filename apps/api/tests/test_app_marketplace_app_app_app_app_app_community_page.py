from app.services.app_marketplace_app_app_app_app_app_community_page import build_community_page

def test_community():
    discussions = [{"title": "How to use webhooks?", "author": "Alice", "replies": 5, "date": "2026-10-01"}]
    contributors = [{"name": "Bob", "contributions": 42, "badge": "🏆"}]
    r = build_community_page(recent_discussions=discussions, top_contributors=contributors)
    assert r["link_count"] == 4
    assert r["total_members"] > 15000
    assert len(r["discussions"]) == 1
    assert len(r["contributors"]) == 1
