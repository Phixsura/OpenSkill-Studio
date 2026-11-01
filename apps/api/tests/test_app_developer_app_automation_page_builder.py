from app.services.app_developer_app_automation_page_builder import build_automations_page

def test_page():
    p = build_automations_page(rules=[{"name": "R1", "enabled": True}, {"name": "R2", "enabled": False}])
    assert p["active"] == 1
    assert p["disabled"] == 1
    assert p["can_add"] is True
