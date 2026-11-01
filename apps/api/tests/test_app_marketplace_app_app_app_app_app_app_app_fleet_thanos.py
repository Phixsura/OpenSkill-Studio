from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_thanos import fleet_thanos_status
def test_thanos():
    r = fleet_thanos_status([{"healthy": True}, {"healthy": True, "compaction_behind": True}])
    assert r["healthy"] == 2
    assert r["compaction_ok"] == 1
