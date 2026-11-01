from app.services.app_marketplace_app_url_shortener import create_short_link, get_link_analytics

def test_create():
    r = create_short_link(url="https://marketplace.openskill.dev/apps/my-app")
    assert r["short_url"].startswith("https://osk.link/")
    assert r["clicks"] == 0

def test_custom_slug():
    r = create_short_link(url="https://example.com", custom_slug="my-app")
    assert r["slug"] == "my-app"

def test_invalid_url():
    r = create_short_link(url="not a url")
    assert "error" in r

def test_invalid_slug():
    r = create_short_link(url="https://x.com", custom_slug="ab")
    assert "error" in r

def test_analytics():
    links = [{"slug": "a", "clicks": 100}, {"slug": "b", "clicks": 50}, {"slug": "c", "clicks": 10}]
    r = get_link_analytics(links=links)
    assert r["total_clicks"] == 160
    assert r["top_links"][0]["slug"] == "a"
