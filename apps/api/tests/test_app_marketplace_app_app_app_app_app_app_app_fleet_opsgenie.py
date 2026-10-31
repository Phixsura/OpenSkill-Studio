from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_opsgenie import fleet_opsgenie_status
def test_og():
    r = fleet_opsgenie_status([{"open_alerts": 5, "avg_close_min": 15, "has_on_call": True}])
    assert r["open_alerts"] == 5
    assert r["responsive"]
