from app.services.app_marketplace_homepage_v3 import build_homepage_v3

def test_personalized():
    h = build_homepage_v3(user={"id": "u1"}, featured=[{"id": "f1"}], trending=[],
                           new_apps=[], collections=[], categories=[], recommended=[{"id": "r1"}],
                           stats={"total_apps": 500})
    assert h["personalized"]
    assert h["sections"][0]["key"] == "recommended"
    assert h["stats_bar"]["apps"] == 500

def test_anonymous():
    h = build_homepage_v3(user=None, featured=[{"id": "f1"}], trending=[], new_apps=[],
                           collections=[], categories=[], recommended=[], stats={})
    assert not h["personalized"]
    assert h["sections"][0]["key"] == "hero"
    assert h["section_count"] == 5
