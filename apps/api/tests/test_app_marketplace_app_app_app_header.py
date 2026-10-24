from app.services.app_marketplace_app_app_app_header import build_header

def test_logged_in():
    r = build_header(user={"name": "Alice Chen", "email": "a@b.com"}, notifications=3)
    assert r["logged_in"]
    assert r["user"]["initials"] == "AC"
    assert r["notifications"] == 3
    assert len(r["nav"]) == 3

def test_logged_out():
    r = build_header()
    assert not r["logged_in"]
    assert r["user"] is None
