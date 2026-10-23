from app.services.app_marketplace_app_app_app_app_app_app_app_user_segmentation import segment_users

def test_segmentation():
    users = [
        {"id": "u1", "actions": 150, "days_since_signup": 90, "days_inactive": 0},
        {"id": "u2", "actions": 5, "days_since_signup": 3, "days_inactive": 0},
        {"id": "u3", "actions": 10, "days_since_signup": 60, "days_inactive": 45},
        {"id": "u4", "actions": 20, "days_since_signup": 30, "days_inactive": 5},
    ]
    r = segment_users(users)
    assert r["total_users"] == 4
    assert "u1" in r["segments"]["power_users"]
    assert "u2" in r["segments"]["new_users"]
    assert "u3" in r["segments"]["churning"]
    assert "u4" in r["segments"]["unclassified"]
    assert r["summary"]["power_users"]["count"] == 1
