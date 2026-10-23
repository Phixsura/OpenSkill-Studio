from app.services.app_marketplace_app_app_step_wizard import build_step_wizard

def test_wizard():
    steps = [
        {"title": "Account", "description": "Set up your account"},
        {"title": "Configure", "description": "App settings"},
        {"title": "Review", "description": "Confirm details"},
    ]
    r = build_step_wizard(steps=steps, current_step=1)
    assert r["total"] == 3
    assert r["current"] == 1
    assert r["steps"][0]["status"] == "completed"
    assert r["steps"][1]["status"] == "current"
    assert r["steps"][2]["status"] == "upcoming"
    assert r["can_go_back"]
    assert r["can_go_next"]
    assert not r["is_final"]
    assert r["progress_pct"] == 33

def test_final():
    r = build_step_wizard(steps=[{"title": "A"}, {"title": "B"}], current_step=1)
    assert r["is_final"]
    assert not r["can_go_next"]
