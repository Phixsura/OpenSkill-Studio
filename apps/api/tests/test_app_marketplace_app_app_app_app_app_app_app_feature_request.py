from app.services.app_marketplace_app_app_app_app_app_app_app_feature_request import FeatureRequestTracker

def test_requests():
    ft = FeatureRequestTracker()
    ft.submit(title="Dark mode", description="Add dark theme", author="alice")
    ft.submit(title="SSO support", description="SAML/OIDC", author="bob")
    ft.vote(1, "bob")
    ft.vote(1, "carol")
    ft.vote(2, "alice")
    top = ft.top_requests()
    assert top[0]["title"] == "Dark mode"
    assert top[0]["votes"] == 2
    r = ft.vote(1, "bob")  # duplicate
    assert "error" in r
    s = ft.stats()
    assert s["total_votes"] == 3
