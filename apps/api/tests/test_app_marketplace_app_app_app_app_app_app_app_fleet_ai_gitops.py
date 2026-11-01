from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gitops import fleet_ai_gitops
def test_go():
    r = fleet_ai_gitops([{"active": True, "repos": 100, "syncs_24h": 500, "out_of_sync": 0}])
    assert r["repos"] == 100
    assert r["synced"]
