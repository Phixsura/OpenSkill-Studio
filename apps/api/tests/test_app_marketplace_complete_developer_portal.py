from app.services.app_marketplace_complete_developer_portal import build_complete_developer_portal

def test_portal():
    p = build_complete_developer_portal(
        developer={"display_name": "DevCo", "slug": "devco", "plan": "pro", "verified": True},
        apps=[{"status": "published", "install_count": 500}, {"status": "draft", "install_count": 0}],
        analytics={"avg_rating": 4.5, "api_calls_today": 10000},
        notifications=[{"read": False}, {"read": True}],
        team=[{"id": "u1"}, {"id": "u2"}],
        billing={"plan": "pro", "past_due": False},
        onboarding={"complete": True},
        health={"grade": "A"}, earnings={"mrr": "$99"},
        compliance={"score": 90, "compliant": True})
    assert p["page_type"] == "complete_developer_portal"
    assert p["dashboard"]["stats"]["published"] == 1
    assert p["dashboard"]["stats"]["installs"] == 500
    assert p["dashboard"]["unread_notifications"] == 1
    assert len(p["pages"]) == 9
    assert not p["alerts"]["has_billing_issue"]
    assert p["quick_metrics"]["mrr"] == "$99"

def test_alerts():
    p = build_complete_developer_portal(
        developer={"display_name": "X"}, apps=[], analytics={},
        notifications=[], team=[], billing={"past_due": True},
        onboarding={"complete": False}, health={"grade": "F"},
        earnings={}, compliance={"score": 20, "compliant": False})
    assert p["alerts"]["has_billing_issue"]
    assert p["alerts"]["has_health_issue"]
    assert p["alerts"]["has_compliance_issue"]
    assert p["alerts"]["onboarding_incomplete"]
