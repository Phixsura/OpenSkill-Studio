from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_descheduler import fleet_descheduler_status
def test_ds():
    r = fleet_descheduler_status([{"pods_evicted": 5, "type": "rebalance"}, {"pods_evicted": 3, "type": "low_utilization"}])
    assert r["pods_evicted"] == 8
    assert r["rebalances"] == 1
