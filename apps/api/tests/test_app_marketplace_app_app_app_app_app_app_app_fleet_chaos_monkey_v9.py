from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chaos_monkey_v9 import fleet_chaos_monkey_v9
def test_monkey_v9():
    r = fleet_chaos_monkey_v9([{"terminated_today": 5, "auto_recovered": 5, "recovery_sec": 30}])
    assert r["terminated_today"] == 5
    assert r["healthy"]
