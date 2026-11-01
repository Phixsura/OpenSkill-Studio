from app.services.app_marketplace_coming_soon import build_coming_soon_page, add_to_waitlist

def test_page():
    p = build_coming_soon_page(feature_name="GraphQL API", description="Native GraphQL", eta="Q1 2027", waitlist_count=500)
    assert p["feature"] == "GraphQL API"
    assert "500" in p["social_proof"]
    assert p["waitlist"]["enabled"]

def test_no_waitlist():
    p = build_coming_soon_page(feature_name="X", description="Y", eta="Q2 2027")
    assert p["social_proof"] is None

def test_join():
    r = add_to_waitlist(email="dev@test.com", feature="graphql")
    assert r["success"]

def test_invalid_email():
    r = add_to_waitlist(email="bad", feature="x")
    assert not r["success"]
