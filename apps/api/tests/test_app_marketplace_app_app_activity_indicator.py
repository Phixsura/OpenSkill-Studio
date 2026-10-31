from app.services.app_marketplace_app_app_activity_indicator import get_user_status

def test_active():
    r = get_user_status(last_active_min_ago=2)
    assert r["status"] == "active"
    assert r["dot"] == "🟢"

def test_idle():
    r = get_user_status(last_active_min_ago=15)
    assert r["status"] == "idle"

def test_offline():
    r = get_user_status(last_active_min_ago=120)
    assert r["status"] == "offline"

def test_manual_dnd():
    r = get_user_status(last_active_min_ago=1, manual_status="dnd")
    assert r["status"] == "dnd"
    assert r["label"] == "Do Not Disturb"
