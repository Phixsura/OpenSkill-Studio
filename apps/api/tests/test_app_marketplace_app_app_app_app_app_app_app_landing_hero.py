from app.services.app_marketplace_app_app_app_app_app_app_app_landing_hero import build_hero

def test_hero():
    r = build_hero(headline="Build Amazing Integrations", subheadline="The developer platform for modern apps")
    assert r["headline"] == "Build Amazing Integrations"
    assert r["cta_primary"] == "Get Started"
    assert len(r["social_proof"]) == 3
    assert r["stats"]["apps"] == "500+"
