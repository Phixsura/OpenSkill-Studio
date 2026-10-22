from app.services.app_marketplace_hero_carousel import build_hero_carousel, build_hero_slide

def test_carousel_limit():
    apps = [{"id": f"a{i}"} for i in range(10)]
    c = build_hero_carousel(apps, slots=3)
    assert len(c) == 3

def test_carousel_few():
    apps = [{"id": "a1"}]
    assert len(build_hero_carousel(apps, slots=3)) == 1

def test_slide():
    s = build_hero_slide({"id": "a1", "name": "Cool App", "slug": "cool-app", "description": "Amazing app", "category": "connector"})
    assert s["name"] == "Cool App"
    assert "cool-app" in s["cta_url"]
