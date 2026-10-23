from app.services.app_marketplace_app_app_hero_section import build_hero

def test_hero():
    r = build_hero(headline="Build Amazing Apps", subheadline="The developer platform",
        cta_primary="Get Started", cta_secondary="Learn More",
        stats=[{"label": "Apps", "value": "500+"}])
    assert r["headline"] == "Build Amazing Apps"
    assert r["has_secondary_cta"]
    assert r["has_stats"]

def test_minimal():
    r = build_hero(headline="Hello", subheadline="World", cta_primary="Go")
    assert not r["has_secondary_cta"]
    assert not r["has_stats"]

def test_xss():
    r = build_hero(headline="<script>", subheadline="ok", cta_primary="Go")
    assert "<script>" not in r["headline"]
