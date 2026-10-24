from app.services.app_marketplace_app_app_app_app_app_app_app_degrade_policy import evaluate_degradation

def test_normal():
    r = evaluate_degradation(30, 0.1, 100, [
        {"name": "high_load", "tier": "moderate", "conditions": [{"metric": "load_pct", "op": "gt", "threshold": 80}],
         "actions": ["shed_non_critical"]}])
    assert r["active_tier"] == "normal"
    assert not r["degraded"]

def test_triggered():
    r = evaluate_degradation(95, 10, 2000, [
        {"name": "overload", "tier": "emergency", "conditions": [{"metric": "load_pct", "op": "gt", "threshold": 90}],
         "actions": ["shed_all", "scale_up"]},
        {"name": "high_errors", "tier": "severe", "conditions": [{"metric": "error_rate", "op": "gt", "threshold": 5}],
         "actions": ["circuit_break"]}])
    assert r["active_tier"] == "emergency"
    assert r["degraded"]
    assert "shed_all" in r["actions"]
