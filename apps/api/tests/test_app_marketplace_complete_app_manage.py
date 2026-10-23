from app.services.app_marketplace_complete_app_manage import build_complete_app_manage

def test_manage():
    r = build_complete_app_manage(
        app={"id": "a1", "name": "SuperApp", "slug": "super-app", "status": "published"},
        version={"version": "2.1.0"}, health={"grade": "A"},
        analytics={"avg_rating": 4.5, "api_calls": 50000},
        webhooks={"count": 3}, team={"count": 5},
        compliance={"compliant": True}, install_stats={"total": 2000, "trend": "up"})
    assert r["page_type"] == "app_management_complete"
    assert len(r["sidebar"]) == 7
    assert len(r["overview_cards"]) == 4
    assert r["overview_cards"][0]["value"] == 2000

def test_compliance_warning():
    r = build_complete_app_manage(
        app={"id": "a1", "name": "X"}, version=None, health={}, analytics={},
        webhooks={"count": 0}, team={"count": 1}, compliance={"compliant": False}, install_stats={})
    compliance_tab = next(s for s in r["sidebar"] if s["key"] == "compliance")
    assert compliance_tab["badge"] == "⚠️"
