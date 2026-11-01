from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_argo_events import fleet_argo_events
def test_ae():
    r = fleet_argo_events([{"active": True, "triggers_24h": 500, "failed_triggers": 2}])
    assert r["triggers_24h"] == 500
    assert r["failed"] == 2
    assert not r["reliable"]
