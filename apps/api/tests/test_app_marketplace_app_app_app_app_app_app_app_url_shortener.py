from app.services.app_marketplace_app_app_app_app_app_app_app_url_shortener import UrlShortener

def test_shorten():
    s = UrlShortener()
    r = s.shorten("https://docs.openskill.io/guides/getting-started", custom_slug="start")
    assert r["slug"] == "start"
    assert "osk.io/start" in r["short_url"]
    resolved = s.resolve("start")
    assert resolved["url"] == "https://docs.openskill.io/guides/getting-started"
    assert resolved["clicks"] == 1
    stats = s.stats("start")
    assert stats["clicks"] == 1

def test_auto_slug():
    s = UrlShortener()
    r = s.shorten("https://example.com/long-path")
    assert len(r["slug"]) == 8

def test_invalid():
    s = UrlShortener()
    r = s.shorten("ftp://bad.com")
    assert "error" in r
