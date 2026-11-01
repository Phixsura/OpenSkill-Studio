from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_datadog import fleet_datadog_status
def test_dd():
    r = fleet_datadog_status([{"active": True, "monitors": 100, "alerts_firing": 3}])
    assert r["monitors"] == 100
    assert not r["calm"]
