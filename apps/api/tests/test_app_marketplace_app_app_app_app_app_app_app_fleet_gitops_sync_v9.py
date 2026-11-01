from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gitops_sync_v9 import fleet_gitops_sync_v9
def test_gitops_v9():
    r = fleet_gitops_sync_v9([{"synced": True, "commits_behind": 0}, {"synced": True, "commits_behind": 0}])
    assert r["synced"] == 2
    assert r["commits_behind"] == 0
    assert r["healthy"]
