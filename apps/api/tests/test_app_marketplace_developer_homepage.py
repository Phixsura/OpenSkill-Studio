from app.services.app_marketplace_developer_homepage import build_developer_homepage

def test_homepage():
    h = build_developer_homepage(
        developer={"display_name": "DevCo", "plan": "pro", "verified": True},
        apps=[{"status": "published"}, {"status": "draft"}],
        stats={"total_installs": 5000, "avg_rating": 4.5, "mrr": "$99"},
        notifications=[{"read": False}, {"read": True}],
        onboarding={"complete": True}, recent_activity=[{"type": "install"}],
        announcements=[{"title": "API v3"}])
    assert h["page_type"] == "developer_homepage"
    assert h["welcome"]["name"] == "DevCo"
    assert h["stats_cards"][0]["value"] == 1  # 1 published
    assert h["onboarding"] is None  # complete
    assert len(h["quick_actions"]) == 4

def test_with_onboarding():
    h = build_developer_homepage(
        developer={"display_name": "New"}, apps=[], stats={},
        notifications=[], onboarding={"complete": False, "pct": 25},
        recent_activity=[], announcements=[])
    assert h["onboarding"] is not None
    assert h["onboarding"]["pct"] == 25
