from app.services.app_marketplace_app_marketplace_homepage_v2 import build_homepage_v2

def test_personalized():
    h = build_homepage_v2(user={"id": "u1"}, featured=[{"name": "A"}], trending=[],
                           recommended=[{"name": "R1"}], new_apps=[], collections=[])
    assert h["personalized"]
    assert h["sections"][0]["key"] == "recommended"

def test_anonymous():
    h = build_homepage_v2(user=None, featured=[{"name": "A"}], trending=[], recommended=[],
                           new_apps=[], collections=[])
    assert not h["personalized"]
    assert h["sections"][0]["key"] == "featured"
