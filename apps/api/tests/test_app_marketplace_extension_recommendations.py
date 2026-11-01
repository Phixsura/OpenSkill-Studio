from app.services.app_marketplace_extension_recommendations import ExtRecommendationsService, ExtInfo

def test_popular_when_no_history():
    svc = ExtRecommendationsService()
    svc.register(ExtInfo("e1", "A", "tools", installs=100))
    svc.register(ExtInfo("e2", "B", "tools", installs=500))
    recs = svc.recommend("new-user")
    assert recs[0].extension_id == "e2"

def test_personalized():
    svc = ExtRecommendationsService()
    svc.register(ExtInfo("e1", "Auth", "security", ["auth"], 100, 4.5))
    svc.register(ExtInfo("e2", "Firewall", "security", ["auth"], 80, 4.0))
    svc.register(ExtInfo("e3", "Charts", "ui", ["viz"], 200, 4.8))
    svc.record_install("u1", "e1")
    recs = svc.recommend("u1")
    assert recs[0].extension_id == "e2"  # same category+tag

def test_similar():
    svc = ExtRecommendationsService()
    svc.register(ExtInfo("e1", "Auth", "security", ["auth", "oauth"]))
    svc.register(ExtInfo("e2", "SSO", "security", ["auth", "sso"]))
    svc.register(ExtInfo("e3", "Charts", "ui", ["viz"]))
    sim = svc.similar("e1")
    assert sim[0].extension_id == "e2"
