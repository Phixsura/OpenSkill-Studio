from app.services.app_marketplace_complete_marketplace_admin import build_complete_marketplace_admin

def test_admin():
    p = build_complete_marketplace_admin(
        platform_stats={"total_apps": 500, "total_developers": 100},
        pending_reviews=[{"id": "r1"}, {"id": "r2"}],
        abuse_reports=[{"id": "a1", "status": "open"}],
        flagged_apps=[{"id": "f1"}],
        system_health={"status": "healthy"})
    assert p["page_type"] == "marketplace_admin"
    assert p["overview"]["pending_reviews"] == 2
    assert p["overview"]["open_abuse_reports"] == 1
    assert len(p["panels"]) == 5

def test_empty():
    p = build_complete_marketplace_admin(
        platform_stats={}, pending_reviews=[], abuse_reports=[], flagged_apps=[], system_health={})
    assert p["overview"]["total_apps"] == 0
