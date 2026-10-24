from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pagerduty import fleet_pagerduty_status
def test_pd():
    r = fleet_pagerduty_status([{"active_incidents": 2, "acknowledged": 1, "avg_ack_min": 5}])
    assert r["active_incidents"] == 2
    assert not r["calm"]
