from app.services.app_marketplace_app_marketplace_developer_app_complete_overview import build_complete_app_overview

def test_overview():
    r = build_complete_app_overview(
        app={"id": "a1", "name": "SuperApp", "status": "published", "current_version": "2.0", "slug": "super-app"},
        health={"score": 95, "status": "healthy"},
        analytics={"installs": 2000, "api_calls": 50000, "engagement_score": 80},
        reviews={"avg_rating": 4.5, "count": 100},
        webhooks={"active": 5, "delivery_rate": 99.5},
        team={"member_count": 3},
        billing={"plan": "pro", "mrr": "$99"},
        compliance={"score": 85, "compliant": True})
    assert r["page_type"] == "app_complete_overview"
    assert r["overall_grade"] in ("A", "B")
    assert len(r["sections"]) == 7
    assert len(r["quick_actions"]) == 4
    assert r["app"]["name"] == "SuperApp"

def test_poor_app():
    r = build_complete_app_overview(
        app={"id": "a2", "name": "BadApp", "status": "draft"},
        health={"score": 30}, analytics={"engagement_score": 20},
        reviews={"avg_rating": 2.0}, webhooks={}, team={},
        billing={}, compliance={"score": 25})
    assert r["overall_grade"] in ("C", "D")
