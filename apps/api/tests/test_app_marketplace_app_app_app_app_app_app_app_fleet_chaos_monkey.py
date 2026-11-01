from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chaos_monkey import fleet_chaos_monkey
def test_monkey():
    r = fleet_chaos_monkey({"enabled": True, "pods_terminated_24h": 10, "survived": 9})
    assert r["survival_rate"] == 90.0
    assert r["enabled"]
