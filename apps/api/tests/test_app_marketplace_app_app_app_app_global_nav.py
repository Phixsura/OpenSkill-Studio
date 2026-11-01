from app.services.app_marketplace_app_app_app_app_global_nav import build_global_nav

def test_logged_in():
    r = build_global_nav(user={"name": "Alice Chen", "email": "a@b.com", "plan": "pro"},
                          active_section="marketplace", notifications=7)
    assert r["logged_in"]
    assert r["user"]["initials"] == "AC"
    assert r["notifications"] == 7
    assert len(r["nav"]) == 4
    assert r["nav"][0]["active"]

def test_logged_out():
    r = build_global_nav()
    assert not r["logged_in"]
    assert r["user"] is None
