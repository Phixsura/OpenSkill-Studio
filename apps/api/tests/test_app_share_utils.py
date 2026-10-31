from app.services.app_share_utils import build_share_links

def test_links():
    s = build_share_links(app_name="Cool App", app_slug="cool-app")
    assert "cool-app" in s["url"]
    assert "twitter.com" in s["twitter"]
    assert "linkedin.com" in s["linkedin"]
    assert "mailto" in s["email"]
    assert "Cool App" in s["copy_text"]
