from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pulsar import fleet_pulsar_status
def test_pulsar():
    r = fleet_pulsar_status([{"healthy": True, "topics": 1000, "msg_per_sec": 100000}])
    assert r["topics"] == 1000
    assert r["all_healthy"]
