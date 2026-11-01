from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gitflow_tracker_v9 import fleet_gitflow_tracker_v9
def test_gf_v9():
    r = fleet_gitflow_tracker_v9([{"open_prs": 5, "merge_queue": 2, "stale_branches": 1}])
    assert r["open_prs"] == 5
    assert r["healthy"]
