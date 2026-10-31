from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_oom import fleet_oom_tracker
def test_oom():
    r = fleet_oom_tracker([{"oom_killed": False, "oom_count": 0}, {"oom_killed": True, "oom_count": 3}])
    assert r["oom_pods"] == 1
    assert r["total_ooms"] == 3
    assert not r["healthy"]
