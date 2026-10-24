from app.services.app_marketplace_app_app_app_app_app_app_app_user_profile_page import build_user_profile

def test_profile():
    r = build_user_profile({
        "name": "Alice Chen", "email": "alice@test.com", "role": "admin",
        "plan": "pro", "joined": "2024-01-15", "org": "Acme Corp",
        "apps": [{"installs": 50000}, {"installs": 30000}],
        "badges": ["verified", "top_rated"],
    })
    assert r["name"] == "Alice Chen"
    assert r["avatar_initials"] == "AC"
    assert r["total_installs"] == 80000
    assert r["installs_display"] == "80,000"
    assert r["app_count"] == 2
    assert len(r["badges"]) == 2
