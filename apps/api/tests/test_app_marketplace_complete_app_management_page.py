from app.services.app_marketplace_complete_app_management_page import build_complete_app_management_page

def test_page():
    p = build_complete_app_management_page(
        installation={"id": "i1", "status": "active"},
        app={"id": "a1", "name": "SuperApp", "current_version": "2.0"},
        config={"timeout": 30}, health={"status": "healthy"},
        usage={"api_calls": 5000}, scheduled_tasks=[{"name": "sync"}],
        feature_flags=[{"key": "dark_mode"}], logs_summary={"total": 100})
    assert p["page_type"] == "app_management"
    assert len(p["tabs"]) == 7
    assert "Tasks (1)" in p["tabs"][4]["title"]
    assert len(p["quick_actions"]) == 4
