from app.services.app_marketplace_complete_onboarding_page import build_complete_onboarding_page

def test_page():
    p = build_complete_onboarding_page(
        developer={"display_name": "New Dev", "email": "dev@test.com"},
        onboarding_status={"progress_pct": 25, "can_publish": False},
        available_templates=[{"id": "t1", "name": "Basic Connector"}],
        tips=["Add a logo", "Write docs"])
    assert p["page_type"] == "developer_onboarding"
    assert len(p["sections"]) == 4
    assert len(p["tips"]) == 2
