from app.services.app_marketplace_app_social_proof import build_social_proof

def test_strong():
    app = {"install_count": 50000, "avg_rating": 4.8, "review_count": 200,
           "verified_developer": True, "featured": True}
    r = build_social_proof(app=app)
    assert r["signal_count"] >= 3
    assert r["trust_score"] >= 60

def test_minimal():
    r = build_social_proof(app={"install_count": 5})
    assert r["signal_count"] == 0
    assert r["trust_score"] == 0

def test_open_source():
    r = build_social_proof(app={"open_source": True, "install_count": 2000})
    assert any(s["type"] == "open_source" for s in r["signals"])
