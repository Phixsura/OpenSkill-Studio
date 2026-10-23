from app.services.app_marketplace_home_page_final import build_home_page_final

def test_authenticated():
    p = build_home_page_final(
        user={"id": "u1"}, hero={"title": "Welcome"}, featured=[{"id": "f1"}],
        trending=[{"id": "t1"}], new_apps=[{"id": "n1"}], categories=[{"id": "c1"}],
        collections=[{"id": "col1"}], spotlight_devs=[{"name": "D1"}],
        stats={"apps": 500, "developers": 100, "installs": 25000},
        recommended=[{"id": "r1"}], blog_posts=[{"title": "Post"}])
    assert p["authenticated"]
    assert p["sections"][0]["key"] == "recommended"
    assert p["section_count"] >= 11

def test_anonymous():
    p = build_home_page_final(
        user=None, hero={}, featured=[], trending=[], new_apps=[],
        categories=[], collections=[], spotlight_devs=[],
        stats={}, recommended=[], blog_posts=[])
    assert not p["authenticated"]
    assert p["sections"][0]["key"] == "hero"
