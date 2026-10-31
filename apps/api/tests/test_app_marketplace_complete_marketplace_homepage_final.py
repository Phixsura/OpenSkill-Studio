from app.services.app_marketplace_complete_marketplace_homepage_final import build_marketplace_homepage_final

def test_authenticated():
    p = build_marketplace_homepage_final(
        user={"id": "u1"}, hero={"title": "Welcome", "subtitle": "Find your next app"},
        featured=[{"id": "f1"}] * 6, trending=[{"id": "t1"}] * 8,
        new_apps=[{"id": "n1"}] * 5, categories=[{"id": "c1"}] * 4,
        collections=[{"id": "col1"}] * 3, stats={"total_apps": 500, "total_developers": 100, "total_installs": 25000},
        spotlight_developers=[{"name": "DevCo"}], recommended=[{"id": "r1"}] * 4)
    assert p["page_type"] == "marketplace_homepage_final"
    assert p["authenticated"]
    assert p["sections"][0]["key"] == "recommended"  # personalized first
    assert p["section_count"] >= 10

def test_anonymous():
    p = build_marketplace_homepage_final(
        user=None, hero={"title": "Marketplace"}, featured=[], trending=[], new_apps=[],
        categories=[], collections=[], stats={}, spotlight_developers=[], recommended=[])
    assert not p["authenticated"]
    assert p["sections"][0]["key"] == "hero"  # no recommended section
