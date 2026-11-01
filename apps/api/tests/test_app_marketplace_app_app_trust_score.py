from app.services.app_marketplace_app_app_trust_score import calculate_trust_score

def test_high_trust():
    signals = {"verified_developer": True, "security_scan_clean": True, "code_signed": True,
               "privacy_policy": True, "responsive_support": True, "high_rating": True,
               "active_maintenance": True, "open_source": True}
    r = calculate_trust_score(signals=signals)
    assert r["score"] == 100
    assert r["trust_level"] == "high"
    assert "Trusted" in r["badge"]

def test_low_trust():
    r = calculate_trust_score(signals={"privacy_policy": True})
    assert r["trust_level"] == "low"
    assert r["score"] == 10

def test_empty():
    r = calculate_trust_score(signals={})
    assert r["score"] == 0
    assert r["met_count"] == 0
