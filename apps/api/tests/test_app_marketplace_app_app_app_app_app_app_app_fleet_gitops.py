from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gitops import fleet_gitops_sync
def test_gitops():
    r = fleet_gitops_sync([{"sync_status": "synced"}, {"sync_status": "out-of-sync"}])
    assert r["synced"] == 1
    assert r["out_of_sync"] == 1
    assert not r["all_synced"]
