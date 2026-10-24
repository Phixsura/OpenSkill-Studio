from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_retention import fleet_data_retention
def test_retention():
    r = fleet_data_retention([{"within_policy": True}, {"within_policy": False}])
    assert r["overdue"] == 1
    assert not r["all_compliant"]
