from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_failover import fleet_failover_status
def test_failover():
    r = fleet_failover_status([{"role": "primary"}, {"role": "standby", "ready": True}, {"role": "standby", "ready": False}])
    assert r["standby_ready"] == 1
    assert r["failover_ready"]
