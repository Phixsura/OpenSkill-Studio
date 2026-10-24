from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_liveness import fleet_liveness_probes
def test_liveness():
    r = fleet_liveness_probes([{"liveness_failures": 0}, {"liveness_failures": 3}, {"liveness_failures": 0}])
    assert r["failing_pods"] == 1
    assert r["total_failures"] == 3
    assert not r["healthy"]
