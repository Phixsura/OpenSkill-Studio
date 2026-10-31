from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_release_train_v9 import fleet_release_train_v9
def test_rt_v9():
    r = fleet_release_train_v9([{"shipped": True, "type": "minor", "lead_time_hours": 4}])
    assert r["shipped"] == 1
    assert r["avg_lead_time_hours"] == 4.0
    assert r["healthy"]
