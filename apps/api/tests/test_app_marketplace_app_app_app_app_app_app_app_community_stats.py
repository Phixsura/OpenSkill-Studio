from app.services.app_marketplace_app_app_app_app_app_app_app_community_stats import compute_community_stats

def test_community():
    r = compute_community_stats(
        forum_posts=500, forum_replies=2000, github_stars=5000, github_forks=800,
        discord_members=3500, twitter_followers=12000,
        blog_posts=45, community_apps=150)
    assert r["forum"]["engagement"] == 2500
    assert r["github"]["stars_display"] == "5,000"
    assert r["social"]["discord_display"] == "3,500"
    assert r["community_score"] == "vibrant"
    assert r["open_source_health"] > 0
