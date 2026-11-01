from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_log_fwd import fleet_log_forwarding
def test_fwd():
    r = fleet_log_forwarding([{"status": "running", "buffer_mb": 10, "dropped_events": 0}, {"status": "running", "buffer_mb": 50, "dropped_events": 100}])
    assert r["healthy"] == 2
    assert r["dropped"] == 100
    assert not r["reliable"]
