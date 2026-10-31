from app.services.app_marketplace_app_app_app_app_app_app_app_infra_cost_rpt import generate_cost_report

def test_report():
    r = generate_cost_report({
        "compute": {"amount": 5000, "change_pct": 10, "forecast": 5500},
        "storage": {"amount": 1200, "change_pct": -5, "forecast": 1140},
        "network": {"amount": 800, "change_pct": 0, "forecast": 800},
    })
    assert r["total"] == 7000
    assert r["top_category"] == "compute"
    assert r["display_total"] == "$7,000.00"
    assert r["forecast_total"] == 7440
