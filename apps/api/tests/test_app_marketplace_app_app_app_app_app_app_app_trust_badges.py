from app.services.app_marketplace_app_app_app_app_app_app_app_trust_badges import get_badges, compute_trust_score

def test_badges():
    r = get_badges(["verified", "security_reviewed", "top_rated"])
    assert len(r) == 3
    assert r[0]["label"] == "Verified Developer"

def test_trust_score():
    r = compute_trust_score(["verified", "security_reviewed", "soc2", "gdpr", "partner"])
    assert r["score"] == 75
    assert r["level"] == "high"
    r2 = compute_trust_score(["verified"])
    assert r2["level"] == "low"
