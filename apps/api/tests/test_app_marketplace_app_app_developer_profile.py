from app.services.app_marketplace_app_app_developer_profile import build_developer_profile

def test_profile():
    r = build_developer_profile(name="Alice", bio="Building great apps",
                                 avatar_email="alice@example.com", apps_count=10,
                                 total_downloads=250000, verified=True,
                                 links={"github": "https://github.com/alice"})
    assert r["name"] == "Alice"
    assert r["verified"]
    assert r["badge"] == "🏆 Top Publisher"
    assert r["downloads_display"] == "250.0K"
    assert "gravatar.com" in r["avatar_url"]

def test_new_developer():
    r = build_developer_profile(name="Bob", apps_count=1, total_downloads=50)
    assert r["badge"] == "👤 Developer"
