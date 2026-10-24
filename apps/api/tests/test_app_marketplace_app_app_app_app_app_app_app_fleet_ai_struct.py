from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_struct import fleet_ai_structured
def test_ais():
    r = fleet_ai_structured([{"active": True, "generations_24h": 1000000, "valid_pct": 99.5}])
    assert r["generations_24h"] == 1000000
    assert r["reliable"]
