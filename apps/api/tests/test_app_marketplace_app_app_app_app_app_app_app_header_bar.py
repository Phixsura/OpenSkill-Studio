from app.services.app_marketplace_app_app_app_app_app_app_app_header_bar import build_header

def test_header():
    r = build_header(user_name="Alice Chen", org_name="Acme", unread_notifications=5, plan="pro")
    assert r["user"]["name"] == "Alice Chen"
    assert r["user"]["initials"] == "AC"
    assert r["org"]["name"] == "Acme"
    assert r["notifications"]["unread"] == 5
    assert r["notifications"]["has_unread"]
    assert r["plan"]["badge"] == "PRO"
    assert not r["plan"]["is_free"]
    assert len(r["nav_links"]) == 3
