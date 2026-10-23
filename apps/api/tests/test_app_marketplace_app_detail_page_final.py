from app.services.app_marketplace_app_detail_page_final import build_app_detail_page_final

def test_full():
    p = build_app_detail_page_final(
        app={"name": "SuperApp", "slug": "super-app", "description": "Great", "category": "connector"},
        developer={"display_name": "DevCo", "slug": "devco", "verified": True},
        version={"version": "2.0"}, reviews={"count": 100, "avg": 4.5},
        stats={"installs": 2000}, screenshots=["s1.png"],
        changelog=[{"version": "2.0"}], related=[{"id": "r1"}],
        badges=[{"label": "Popular"}], pricing={"plan": "free"},
        installed=False, wishlisted=True, support={"email": "help@app.com"},
        faq=[{"q": "How?"}])
    assert p["page_type"] == "app_detail_page_final"
    assert len(p["tabs"]) == 5  # includes pricing
    assert p["hero"]["cta"]["wishlisted"]
    assert not p["hero"]["cta"]["installed"]

def test_minimal():
    p = build_app_detail_page_final(
        app={"name": "App"}, developer={}, version=None, reviews={"count": 0},
        stats={}, screenshots=[], changelog=[], related=[], badges=[],
        pricing=None, installed=True, wishlisted=False, support={}, faq=[])
    assert len(p["tabs"]) == 4  # no pricing
    assert p["hero"]["cta"]["installed"]
