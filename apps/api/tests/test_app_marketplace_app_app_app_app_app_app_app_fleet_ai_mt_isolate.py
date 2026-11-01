from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_mt_isolate import fleet_ai_mt_isolation
def test_mt():
    r = fleet_ai_mt_isolation([{"active": True, "tenants": 1000, "isolated": 1000, "breaches": 0}])
    assert r["tenants"] == 1000
    assert r["secure"]
