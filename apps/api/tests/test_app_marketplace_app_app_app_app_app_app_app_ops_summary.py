from app.services.app_marketplace_app_app_app_app_app_app_app_ops_summary import generate_ops_summary

def test_nominal():
    r = generate_ops_summary({"uptime_pct": 99.99, "deploys_today": 5, "open_incidents": 0, "error_rate": 0.1})
    assert r["status"] == "nominal"
    assert r["risk_level"] == "low"

def test_elevated():
    r = generate_ops_summary({"open_incidents": 2, "error_rate": 2.5})
    assert r["status"] == "elevated"
