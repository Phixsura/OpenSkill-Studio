from app.services.app_marketplace_app_app_app_app_app_app_app_rightsize import analyze_rightsizing

def test_rightsize():
    r = analyze_rightsizing([
        {"name": "idle-vm", "cpu_avg_pct": 5, "mem_avg_pct": 10, "monthly_cost": 200},
        {"name": "busy-vm", "cpu_avg_pct": 80, "mem_avg_pct": 70, "monthly_cost": 500},
        {"name": "light-vm", "cpu_avg_pct": 25, "mem_avg_pct": 30, "monthly_cost": 100},
    ])
    assert r["count"] == 2  # idle + light
    assert r["total_savings"] > 0
