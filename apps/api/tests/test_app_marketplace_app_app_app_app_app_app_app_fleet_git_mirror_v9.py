from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_git_mirror_v9 import fleet_git_mirror_v9
def test_gm_v9():
    r = fleet_git_mirror_v9([{"synced": True, "commits_behind": 0, "repo": "main"}])
    assert r["synced"] == 1
    assert r["healthy"]
