from app.services.app_marketplace_app_app_app_user_profile_page import build_user_profile_page

def test_profile():
    user = {"name": "Alice Chen", "email": "alice@example.com", "bio": "Builder", "member_since": "2024-01-01"}
    apps = [{"id": "a1", "name": "SuperApp", "icon": "🚀", "installs": 5000}]
    r = build_user_profile_page(user=user, apps=apps, activity_count=150)
    assert r["name"] == "Alice Chen"
    assert r["stats"]["apps"] == 1
    assert r["stats"]["total_installs"] == 5000
    assert len(r["recent_apps"]) == 1
    assert "gravatar.com" in r["avatar_url"]
