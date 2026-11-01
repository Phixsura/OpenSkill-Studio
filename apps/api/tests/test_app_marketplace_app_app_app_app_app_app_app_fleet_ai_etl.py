from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_etl import fleet_ai_etl
def test_etl():
    r = fleet_ai_etl([{"active": True, "jobs_24h": 500, "records": 100000000, "failures": 0}])
    assert r["jobs_24h"] == 500
    assert r["reliable"]
