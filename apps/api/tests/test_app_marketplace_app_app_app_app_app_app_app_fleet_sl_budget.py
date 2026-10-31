from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sl_budget import fleet_sl_budget
def test_budget():
    r = fleet_sl_budget([{"remaining_pct": 50}, {"remaining_pct": 10}, {"remaining_pct": -5}])
    assert r["exhausted"] == 1
    assert r["low"] == 1
    assert r["alert"]
