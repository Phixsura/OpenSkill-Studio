from app.services.app_marketplace_app_app_cost_alert import evaluate_cost_alerts

def test_ok():
    r = evaluate_cost_alerts(current_spend=200, budget=1000, daily_spend=10, days_remaining=20)
    assert r["status"] == "ok"
    assert len(r["alerts"]) == 0

def test_warning():
    r = evaluate_cost_alerts(current_spend=800, budget=1000, daily_spend=20, days_remaining=15)
    assert r["status"] == "warning"
    assert r["projected_overage"] > 0

def test_critical():
    r = evaluate_cost_alerts(current_spend=1100, budget=1000, daily_spend=10, days_remaining=5)
    assert r["status"] == "critical"
    assert any(a["level"] == "critical" for a in r["alerts"])
