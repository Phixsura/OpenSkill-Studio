from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_capacity import plan_fleet_capacity
def test_plan():
    r = plan_fleet_capacity([{"cpu_pct": 80}, {"cpu_pct": 90}])
    assert r["avg_cpu_pct"] == 85
    assert r["headroom_pct"] == 15
    assert r["needs_scaling"]
