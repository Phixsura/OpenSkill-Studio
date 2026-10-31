from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_req_prio import fleet_request_priority
def test_prio():
    r = fleet_request_priority([{"priority": "critical"}, {"priority": "high"}, {"priority": "normal"}, {"priority": "low"}])
    assert r["high_priority_pct"] == 50.0
