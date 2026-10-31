from app.services.app_marketplace_app_app_app_app_app_app_app_cost_efficiency import score_efficiency

def test_efficient():
    r = score_efficiency([
        {"name": "api-1", "cost": 100, "utilization_pct": 70},
        {"name": "api-2", "cost": 100, "utilization_pct": 80},
    ])
    assert r["score"] > 70
    assert len(r["wasteful_resources"]) == 0

def test_wasteful():
    r = score_efficiency([
        {"name": "idle-vm", "cost": 500, "utilization_pct": 5},
        {"name": "busy-vm", "cost": 200, "utilization_pct": 85},
    ])
    assert len(r["wasteful_resources"]) == 1
    assert r["potential_savings"] > 0
    assert r["wasteful_resources"][0]["name"] == "idle-vm"
