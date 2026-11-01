from app.services.app_marketplace_app_store_provider import (
    AppStoreProvider, StoreListing,
)


def _setup() -> AppStoreProvider:
    sp = AppStoreProvider()
    sp.add_listing(StoreListing("s1", "Slack Bot", "💬", "alice", "2.0.0", "Slack integration", "messaging", ["slack"], 5000, 4.8, 50, verified=True))
    sp.add_listing(StoreListing("g1", "GitHub Sync", "🐙", "bob", "1.5.0", "Sync with GitHub", "scm", ["github", "git"], 8000, 4.5, 30))
    sp.add_listing(StoreListing("t1", "Dark Theme", "🎨", "carol", "3.0.0", "Beautiful dark theme", "themes", ["theme", "dark"], 12000, 4.9, 100))
    sp.add_listing(StoreListing("a1", "Auto Deploy", "🚀", "dave", "1.0.0", "Automated deployments", "automation", ["deploy", "ci"], 2000, 3.8, 2))
    return sp


def test_search():
    sp = _setup()
    results = sp.search("slack")
    assert len(results) == 1
    assert results[0].extension_id == "s1"


def test_search_by_category():
    sp = _setup()
    results = sp.search("", category="themes")
    assert all(r.category == "themes" for r in results)


def test_trending():
    sp = _setup()
    trending = sp.get_trending(3)
    assert trending[0].extension_id == "t1"  # most downloads


def test_top_rated():
    sp = _setup()
    top = sp.get_top_rated()
    assert top[0].rating >= top[-1].rating
    # a1 excluded: only 2 reviews (< 3 minimum)
    assert all(r.extension_id != "a1" for r in top)


def test_featured():
    sp = _setup()
    sp.set_featured(["s1", "t1"])
    featured = sp.get_featured()
    assert len(featured) == 2


def test_collections():
    sp = _setup()
    coll = sp.create_collection("best-tools", "Best Tools", "Our top picks", ["s1", "g1"])
    assert len(coll.items) == 2
    assert sp.get_collection("best-tools") is not None


def test_store_home():
    sp = _setup()
    sp.set_featured(["t1"])
    home = sp.get_store_home()
    assert home["total_extensions"] == 4
    assert len(home["featured"]) == 1
    assert len(home["trending"]) >= 1
