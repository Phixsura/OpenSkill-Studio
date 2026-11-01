from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_req_valid import fleet_ai_request_validator
def test_rv():
    r = fleet_ai_request_validator([{"active": True, "validated_24h": 100000000, "rejected": 50000, "schemas": 200}])
    assert r["validated_24h"] == 100000000
    assert r["strict"]
