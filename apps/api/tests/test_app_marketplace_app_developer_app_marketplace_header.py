from app.services.app_marketplace_app_developer_app_marketplace_header import build_marketplace_header

def test_anonymous():
    h = build_marketplace_header(user=None)
    assert len(h["nav_items"]) == 3
    assert h["user"] is None

def test_logged_in():
    h = build_marketplace_header(user={"display_name": "Alice", "is_developer": True}, notification_count=5)
    assert len(h["nav_items"]) == 4
    assert h["user"]["name"] == "Alice"
    assert h["notification_count"] == 5
    assert h["is_developer"]
