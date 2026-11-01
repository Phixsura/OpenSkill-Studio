from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_surrealdb import fleet_surrealdb_status
def test_sdb():
    r = fleet_surrealdb_status([{"running": True, "namespaces": 5, "tables": 100}])
    assert r["tables"] == 100
    assert r["all_running"]
