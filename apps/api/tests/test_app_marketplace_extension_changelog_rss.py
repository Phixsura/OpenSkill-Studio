from app.services.app_marketplace_extension_changelog_rss import (
    ChangelogRSSGenerator, ChangelogItem,
)


def _setup() -> ChangelogRSSGenerator:
    gen = ChangelogRSSGenerator()
    gen.add_entry("ext-1", ChangelogItem("1.0.0", "Initial Release", "First version", "2026-10-01", "alice"))
    gen.add_entry("ext-1", ChangelogItem("1.1.0", "New Features", "Added search and filters", "2026-10-15", "alice"))
    gen.add_entry("ext-1", ChangelogItem("2.0.0", "Major Update", "Complete redesign", "2026-10-25", "bob"))
    return gen


def test_generate_rss():
    gen = _setup()
    rss = gen.generate_rss("ext-1", "Slack Bot Changelog")
    assert '<?xml version="1.0"' in rss
    assert '<rss version="2.0">' in rss
    assert "Slack Bot Changelog" in rss
    assert "Initial Release" in rss
    assert "Major Update" in rss


def test_rss_escaping():
    gen = ChangelogRSSGenerator()
    gen.add_entry("ext-2", ChangelogItem("1.0", "Fix <script>", "Fix & improve", "2026-10-01", "dev"))
    rss = gen.generate_rss("ext-2")
    assert "&lt;script&gt;" in rss
    assert "&amp;" in rss


def test_json_feed():
    gen = _setup()
    feed = gen.generate_json_feed("ext-1")
    assert feed["version"] == "https://jsonfeed.org/version/1.1"
    assert len(feed["items"]) == 3
    assert feed["items"][0]["id"] == "2.0.0"  # newest first


def test_latest():
    gen = _setup()
    latest = gen.get_latest("ext-1")
    assert latest is not None
    assert latest.version == "2.0.0"


def test_feed_urls():
    gen = ChangelogRSSGenerator()
    urls = gen.get_feed_urls("ext-3")
    assert "feed.xml" in urls["rss"]
    assert "feed.json" in urls["json"]


def test_empty_feed():
    gen = ChangelogRSSGenerator()
    rss = gen.generate_rss("empty")
    assert "<channel>" in rss
    assert "<item>" not in rss
