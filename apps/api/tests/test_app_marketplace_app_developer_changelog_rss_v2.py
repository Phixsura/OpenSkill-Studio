from app.services.app_marketplace_app_developer_changelog_rss_v2 import build_developer_feed, compute_release_frequency

def test_feed():
    updates = [{"app_name": "App1", "version": "2.0", "app_slug": "app1", "released_at": "2026-06-01"},
               {"app_name": "App2", "version": "1.0", "app_slug": "app2", "released_at": "2026-07-01"}]
    f = build_developer_feed(developer={"display_name": "DevCo"}, app_updates=updates)
    assert f["entries"][0]["app_slug"] == "app2"  # newest first
    assert "DevCo" in f["feed_title"]

def test_frequency():
    releases = [{"released_at": f"2026-{i:02d}-01"} for i in range(1, 13)]
    r = compute_release_frequency(releases=releases)
    assert r["frequency"] == "monthly"
