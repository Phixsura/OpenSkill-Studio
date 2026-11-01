from app.services.app_marketplace_app_social_sharing import build_share_links, track_share, get_share_stats

def test_links():
    r = build_share_links(app={"id": "a1", "name": "MyApp", "slug": "my-app"})
    assert "twitter.com" in r["twitter"]
    assert "my-app" in r["url"]

def test_track():
    r = track_share(app_id="a1", platform="twitter")
    assert r["tracked"]

def test_stats():
    shares = [{"platform": "twitter"}, {"platform": "twitter"}, {"platform": "linkedin"}]
    s = get_share_stats(shares=shares)
    assert s["total"] == 3
    assert s["by_platform"]["twitter"] == 2
