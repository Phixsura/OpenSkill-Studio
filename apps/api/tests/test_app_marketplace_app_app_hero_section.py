from app.services.app_marketplace_app_app_hero_section import build_hero

def test_hero():
    r = build_hero(title="Build apps faster", subtitle="The developer platform",
                   cta_primary={"label": "Get Started", "href": "/signup"},
                   cta_secondary={"label": "View Docs", "href": "/docs"},
                   badge="New: SDK v3",
                   stats=[{"value": "5K+", "label": "Apps"}, {"value": "100K+", "label": "Developers"}])
    assert r["title"] == "Build apps faster"
    assert r["cta_primary"]["label"] == "Get Started"
    assert r["badge"] == "New: SDK v3"
    assert len(r["stats"]) == 2
