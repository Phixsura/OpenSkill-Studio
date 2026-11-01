from app.services.app_marketplace_app_app_app_app_app_app_app_env_promote import create_promotion, promotion_pipeline

def test_promote():
    r = create_promotion("2.0", "staging", "production")
    assert r["valid"]
    assert r["requires_approval"]
    r2 = create_promotion("2.0", "production", "staging")
    assert not r2["valid"]

def test_pipeline():
    r = promotion_pipeline("3.0")
    assert r["environments"] == 3
    assert r["pipeline"][0]["status"] == "deployed"
    assert r["pipeline"][2]["requires_approval"]
