from app.services.app_marketplace_app_app_url_shortener import shorten_url, build_link_analytics

def test_shorten():
    r = shorten_url(url="https://example.com/very/long/path")
    assert r["short"].startswith("https://osk.li/")
    assert len(r["slug"]) == 8

def test_custom_slug():
    r = shorten_url(url="https://example.com", custom_slug="myapp")
    assert r["slug"] == "myapp"

def test_bad_scheme():
    r = shorten_url(url="javascript:alert(1)")
    assert "error" in r

def test_analytics():
    links = [
        {"slug": "abc", "original": "https://a.com", "clicks": 100},
        {"slug": "def", "original": "https://b.com", "clicks": 250},
    ]
    r = build_link_analytics(links=links)
    assert r["total_clicks"] == 350
    assert r["links"][0]["clicks"] == 250  # sorted desc
