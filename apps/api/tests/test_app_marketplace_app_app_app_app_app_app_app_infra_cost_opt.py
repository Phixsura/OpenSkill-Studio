from app.services.app_marketplace_app_app_app_app_app_app_app_infra_cost_opt import analyze_resources, reserved_vs_ondemand

def test_analyze():
    r = analyze_resources([
        {"name": "idle-vm", "type": "vm", "monthly_cost": 100, "utilization_pct": 5},
        {"name": "busy-vm", "type": "vm", "monthly_cost": 200, "utilization_pct": 85},
        {"name": "low-vm", "type": "vm", "monthly_cost": 150, "utilization_pct": 30},
    ])
    assert r["resources_analyzed"] == 3
    assert len(r["opportunities"]) == 2
    assert r["potential_savings"] > 0
    assert r["opportunities"][0]["resource"] == "idle-vm"

def test_reserved():
    r = reserved_vs_ondemand([
        {"pricing": "on_demand", "monthly_cost": 100},
        {"pricing": "on_demand", "monthly_cost": 100},
        {"pricing": "reserved", "monthly_cost": 60},
    ])
    assert r["recommendation"] == "increase_reserved"
