from app.services.app_marketplace_app_app_app_app_app_app_app_activity_counter import compute_active_users

def test_active():
    events = [
        {"user_id": "u1", "period": "daily"}, {"user_id": "u2", "period": "daily"},
        {"user_id": "u3", "period": "weekly"}, {"user_id": "u4", "period": "weekly"},
        {"user_id": "u5", "period": "monthly"}, {"user_id": "u6", "period": "monthly"},
    ]
    r = compute_active_users(events)
    assert r["dau"] == 2
    assert r["wau"] == 4  # 2 daily + 2 weekly
    assert r["mau"] == 6  # all
    assert r["stickiness"] > 0
