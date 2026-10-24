from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_redshift import fleet_redshift_status
def test_rs():
    r = fleet_redshift_status([{"status": "available", "nodes": 8, "storage_pct": 60}])
    assert r["nodes"] == 8
    assert r["healthy"]
