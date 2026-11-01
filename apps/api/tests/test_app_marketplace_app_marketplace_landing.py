from app.services.app_marketplace_app_marketplace_landing import build_landing_page, build_testimonial

def test_landing():
    p = build_landing_page(
        hero={"title": "Build Better", "subtitle": "With OpenSkill"},
        featured_apps=[{"id": "a1"}], categories=[{"id": "connector"}],
        stats={"apps": 500, "developers": 100, "installs": 25000},
        testimonials=[{"author": "Alice", "quote": "Amazing!"}],
        cta={"title": "Start Now", "button": "Sign Up"})
    assert p["page_type"] == "marketplace_landing"
    assert len(p["sections"]) == 5
    assert p["hero"]["title"] == "Build Better"

def test_testimonial():
    t = build_testimonial(author="Alice", role="CTO", company="Acme", quote="Best platform", rating=5)
    assert t["avatar_initial"] == "A"
    assert t["rating"] == 5
