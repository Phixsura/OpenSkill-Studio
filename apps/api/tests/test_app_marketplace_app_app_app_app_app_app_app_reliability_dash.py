from app.services.app_marketplace_app_app_app_app_app_app_app_reliability_dash import build_reliability_dashboard

def test_dashboard():
    r = build_reliability_dashboard({
        "mttr_min": 15, "mtbf_hours": 720, "change_failure_pct": 2, "uptime_pct": 99.95})
    assert r["maturity"] == "advanced"
    assert r["reliability_score"] > 85

def test_basic():
    r = build_reliability_dashboard({
        "mttr_min": 120, "mtbf_hours": 24, "change_failure_pct": 25, "uptime_pct": 95})
    assert r["maturity"] in ("basic", "intermediate")
