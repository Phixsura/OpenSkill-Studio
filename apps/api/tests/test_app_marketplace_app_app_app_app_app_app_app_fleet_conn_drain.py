from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_conn_drain import fleet_conn_draining
def test_drain():
    r = fleet_conn_draining([{"draining": True, "drain_time_sec": 30}, {"draining": False}])
    assert r["draining"] == 1
    assert r["avg_drain_sec"] == 30.0
    assert not r["all_drained"]
