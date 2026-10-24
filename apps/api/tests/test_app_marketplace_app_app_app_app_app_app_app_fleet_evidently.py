from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_evidently import fleet_evidently_status
def test_ev():
    r = fleet_evidently_status([{"active": True, "reports_24h": 100, "drift_alerts": 2}])
    assert r["reports_24h"] == 100
    assert not r["stable"]
