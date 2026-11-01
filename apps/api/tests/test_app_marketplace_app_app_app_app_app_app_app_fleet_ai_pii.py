from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_pii import fleet_ai_pii
def test_pii():
    r = fleet_ai_pii([{"active": True, "docs_24h": 1000000, "pii_found_24h": 50000, "redacted_24h": 50000}])
    assert r["all_redacted"]
