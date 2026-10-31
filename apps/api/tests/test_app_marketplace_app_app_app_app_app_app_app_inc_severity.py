from app.services.app_marketplace_app_app_app_app_app_app_app_inc_severity import classify_severity, severity_distribution

def test_classify():
    r = classify_severity(["data_loss", "slow_response"])
    assert r["severity"] == "critical"
    assert r["escalate"]
    assert r["response_time_min"] == 15

def test_low():
    r = classify_severity(["cosmetic"])
    assert r["severity"] == "low"
    assert not r["escalate"]

def test_distribution():
    r = severity_distribution([{"severity": "critical"}, {"severity": "high"},
                                  {"severity": "low"}, {"severity": "low"}])
    assert r["total"] == 4
    assert r["critical_pct"] == 25
