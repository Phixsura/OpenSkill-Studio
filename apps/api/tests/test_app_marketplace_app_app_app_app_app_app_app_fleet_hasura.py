from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hasura import fleet_hasura_status
def test_hasura():
    r = fleet_hasura_status([{"healthy": True, "tables": 100, "requests_24h": 5000000}])
    assert r["tables"] == 100
    assert r["all_healthy"]
