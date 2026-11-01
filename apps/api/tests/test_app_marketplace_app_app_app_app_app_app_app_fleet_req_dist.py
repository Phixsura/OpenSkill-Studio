from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_req_dist import fleet_request_distribution
def test_dist():
    r = fleet_request_distribution([{"region": "us-east", "requests": 6000}, {"region": "eu-west", "requests": 4000}])
    assert r["total_requests"] == 10000
    assert r["distribution"]["us-east"] == 60.0
    assert r["hotspot"] == "us-east"
