from app.services.app_marketplace_user_segment import classify_user, build_segment_summary

def test_new_power():
    r = classify_user(user={"id": "u1", "days_since_signup": 3, "install_count": 15, "review_count": 0, "total_spend": 0})
    assert "new_user" in r["segments"]
    assert "power_user" in r["segments"]

def test_established_premium():
    r = classify_user(user={"id": "u2", "days_since_signup": 90, "install_count": 5, "total_spend": 200, "is_developer": True})
    assert "established" in r["segments"]
    assert "premium" in r["segments"]
    assert "developer" in r["segments"]

def test_summary():
    users = [
        {"id": "u1", "days_since_signup": 3, "install_count": 1},
        {"id": "u2", "days_since_signup": 60, "install_count": 10, "total_spend": 50},
    ]
    r = build_segment_summary(users=users)
    assert r["total_users"] == 2
    assert any(s["name"] == "power_user" for s in r["segments"])
