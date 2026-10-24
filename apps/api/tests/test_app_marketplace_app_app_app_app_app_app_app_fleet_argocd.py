from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_argocd import fleet_argocd_sync
def test_argo():
    r = fleet_argocd_sync([{"sync_status": "Synced", "health_status": "Healthy"}, {"sync_status": "OutOfSync", "health_status": "Degraded"}])
    assert r["synced"] == 1
    assert r["degraded"] == 1
    assert not r["all_synced"]
