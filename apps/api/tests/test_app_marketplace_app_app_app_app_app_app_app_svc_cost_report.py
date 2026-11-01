from app.services.app_marketplace_app_app_app_app_app_app_app_svc_cost_report import generate_cost_report

def test_report():
    r = generate_cost_report([
        {"name": "api", "monthly_cost": 500, "team": "platform"},
        {"name": "db", "monthly_cost": 300, "team": "data"},
        {"name": "cache", "monthly_cost": 200, "team": "platform"},
    ])
    assert r["total_cost"] == 1000
    assert r["services"][0]["service"] == "api"
    assert r["services"][0]["share_pct"] == 50.0
