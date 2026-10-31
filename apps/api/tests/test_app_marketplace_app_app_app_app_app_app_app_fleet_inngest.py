from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_inngest import fleet_inngest_status
def test_ig():
    r = fleet_inngest_status([{"active": True, "functions": 50, "events_24h": 100000}])
    assert r["functions"] == 50
    assert r["all_active"]
