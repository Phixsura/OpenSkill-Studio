from app.services.app_marketplace_complete_developer_portal_final import build_developer_portal_final

def test_portal():
    p = build_developer_portal_final(
        developer={"display_name": "DevCo", "plan": "pro", "verified": True},
        apps=[{"status": "published", "install_count": 500}, {"status": "draft", "install_count": 0}],
        analytics={"avg_rating": 4.5}, notifications=[{"read": False}, {"read": True}],
        team=[{"id": "u1"}, {"id": "u2"}], billing={"plan": "pro", "past_due": False},
        earnings={"mrr": "$99"}, onboarding={"complete": True},
        health={"grade": "A"}, compliance={"score": 90, "compliant": True},
        feature_flags=[{"enabled": True}, {"enabled": False}])
    assert p["page_type"] == "developer_portal_final"
    assert p["dashboard"]["stats"][0]["value"] == 1  # 1 published
    assert p["dashboard"]["unread_notifications"] == 1
    assert len(p["navigation"]) == 10
    assert not p["alerts"]["billing_issue"]
    assert p["onboarding"] is None  # complete

def test_alerts():
    p = build_developer_portal_final(
        developer={"display_name": "X"}, apps=[], analytics={}, notifications=[],
        team=[], billing={"past_due": True}, earnings={},
        onboarding={"complete": False}, health={"grade": "F"},
        compliance={"compliant": False}, feature_flags=[])
    assert p["alerts"]["billing_issue"]
    assert p["alerts"]["health_issue"]
    assert p["alerts"]["compliance_issue"]
    assert p["alerts"]["onboarding_incomplete"]
    assert p["onboarding"] is not None
