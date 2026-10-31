from app.services.app_marketplace_complete_marketplace_admin_page import build_complete_admin_page

def test_admin():
    p = build_complete_admin_page(
        platform_stats={"total_apps": 500, "total_developers": 100},
        pending_reviews=[{"id": "r1"}, {"id": "r2"}],
        abuse_reports=[{"id": "a1", "status": "open"}],
        flagged_apps=[{"id": "f1"}],
        system_health={"status": "healthy"},
        recent_actions=[{"type": "approved_app"}])
    assert p["overview"]["pending_reviews"] == 2
    assert p["overview"]["open_reports"] == 1
    assert len(p["priority_queue"]) == 3
    assert len(p["quick_actions"]) == 4
