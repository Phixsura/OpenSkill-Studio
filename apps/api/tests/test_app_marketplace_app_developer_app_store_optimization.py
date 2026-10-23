from app.services.app_marketplace_app_developer_app_store_optimization import analyze_listing, suggest_keywords

def test_good_listing():
    app = {"name": "My Great App", "description": "A" * 150, "icon": "icon.png",
           "screenshots": ["s1", "s2", "s3"], "tags": ["a", "b", "c"],
           "documentation_url": "https://docs.example.com", "support_email": "help@example.com"}
    r = analyze_listing(app=app)
    assert r["score"] == 100
    assert r["grade"] == "A"

def test_poor_listing():
    r = analyze_listing(app={"name": "X", "description": "Short"})
    assert r["grade"] in ("C", "D")
    assert len(r["suggestions"]) > 3

def test_keywords():
    k = suggest_keywords(category="connector", description="Powerful data synchronization engine")
    assert "integration" in k
    assert "sync" in k
