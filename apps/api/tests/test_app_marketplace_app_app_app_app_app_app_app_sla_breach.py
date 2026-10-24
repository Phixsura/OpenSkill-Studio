from app.services.app_marketplace_app_app_app_app_app_app_app_sla_breach import detect_breaches, breach_impact

def test_no_breach():
    r = detect_breaches([
        {"name": "api", "sla_target": 99.9, "uptime_pct": 99.99},
    ])
    assert r["all_met"]

def test_breach():
    r = detect_breaches([
        {"name": "api", "sla_target": 99.9, "uptime_pct": 99.99},
        {"name": "db", "sla_target": 99.9, "uptime_pct": 98.5},
    ])
    assert r["breached"] == 1
    assert r["breaches"][0]["service"] == "db"
    assert r["breaches"][0]["severity"] == "critical"

def test_impact():
    r = breach_impact({"service": "db", "gap": 1.4}, monthly_revenue=100000)
    assert r["sla_credit_pct"] == 14
    assert r["estimated_credit"] == 14000
