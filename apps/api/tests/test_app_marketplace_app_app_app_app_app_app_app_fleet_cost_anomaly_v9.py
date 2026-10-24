from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_anomaly_v9 import fleet_cost_anomaly_v9
def test_cost_v9():
    r = fleet_cost_anomaly_v9([{"amount": 100}, {"amount": 110}, {"amount": 95}])
    assert r["total_bills"] == 3
    assert r["anomalies"] == 0
    assert r["healthy"]
