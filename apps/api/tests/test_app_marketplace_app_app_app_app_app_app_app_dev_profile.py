from app.services.app_marketplace_app_app_app_app_app_app_app_dev_profile import build_developer_profile

def test_profile():
    r = build_developer_profile({
        "name": "Acme Corp", "bio": "We build developer tools",
        "verified": True, "joined": "2024-01-01",
        "apps": [
            {"name": "Slack Bot", "icon": "💬", "rating": 4.8, "installs": 50000},
            {"name": "GitHub Sync", "icon": "🐙", "rating": 4.5, "installs": 30000},
        ]
    })
    assert r["name"] == "Acme Corp"
    assert r["verified"]
    assert r["app_count"] == 2
    assert r["total_installs"] == 80000
    assert r["avg_rating"] == 4.7
    assert r["total_installs_display"] == "80,000"
