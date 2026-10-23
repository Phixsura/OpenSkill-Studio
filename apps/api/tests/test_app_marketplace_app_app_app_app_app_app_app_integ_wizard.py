from app.services.app_marketplace_app_app_app_app_app_app_app_integ_wizard import get_integration, build_wizard, list_integrations

def test_integration():
    i = get_integration("slack")
    assert i["name"] == "Slack"
    assert i["step_count"] == 4

def test_wizard():
    r = build_wizard("github", current_step=2)
    assert r["name"] == "GitHub"
    assert r["progress_pct"] == 50
    assert r["steps"][0]["status"] == "completed"
    assert r["steps"][2]["status"] == "current"
    assert not r["complete"]

def test_list():
    assert len(list_integrations()) == 4
