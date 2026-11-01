from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cosmosdb import fleet_cosmosdb_status
def test_cosmos():
    r = fleet_cosmosdb_status([{"status": "Online", "consumed_ru_per_sec": 50000, "regions": ["eastus", "westeu", "apeast"]}])
    assert r["regions"] == 3
    assert r["globally_distributed"]
