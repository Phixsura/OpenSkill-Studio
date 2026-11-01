from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cas import fleet_cluster_autoscaler
def test_cas():
    r = fleet_cluster_autoscaler([{"action": "scale_up", "status": "ok"}, {"action": "scale_down", "status": "failed"}])
    assert r["scale_ups"] == 1
    assert r["failed"] == 1
    assert not r["healthy"]
