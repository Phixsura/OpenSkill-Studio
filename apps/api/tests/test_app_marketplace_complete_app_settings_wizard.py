from app.services.app_marketplace_complete_app_settings_wizard import build_settings_wizard

def test_wizard_start():
    w = build_settings_wizard(app={"id": "a1"})
    assert w["current_step"] == 0
    assert w["progress_pct"] == 0
    assert not w["can_submit"]

def test_wizard_middle():
    w = build_settings_wizard(app={"id": "a1"}, current_step=2)
    assert w["steps"][0]["status"] == "completed"
    assert w["steps"][2]["status"] == "current"
    assert w["steps"][3]["status"] == "pending"

def test_wizard_end():
    w = build_settings_wizard(app={"id": "a1"}, current_step=4)
    assert w["can_submit"]
    assert w["progress_pct"] == 80
