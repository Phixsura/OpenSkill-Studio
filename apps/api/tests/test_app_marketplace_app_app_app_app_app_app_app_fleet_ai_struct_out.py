from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_struct_out import fleet_ai_structured_output
def test_so():
    r = fleet_ai_structured_output([{"active": True, "requests_24h": 2000000, "valid_pct": 99.8, "schemas": 150}])
    assert r["valid_pct"] == 99.8
    assert r["reliable"]
