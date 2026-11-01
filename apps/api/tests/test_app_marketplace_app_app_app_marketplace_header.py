from app.services.app_marketplace_app_app_app_marketplace_header import build_marketplace_header

def test_header():
    r = build_marketplace_header(user={"name": "Alice Chen", "plan": "pro"},
                                  notifications=5, active_path="/marketplace")
    assert r["logged_in"]
    assert r["user"]["initials"] == "AC"
    assert r["notifications"] == 5
    assert len(r["nav"]) == 5
    assert r["nav"][0]["active"]

def test_logged_out():
    r = build_marketplace_header()
    assert not r["logged_in"]
