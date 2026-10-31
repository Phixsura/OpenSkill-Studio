from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_timescaledb import fleet_timescaledb_status
def test_ts():
    r = fleet_timescaledb_status([{"healthy": True, "chunks": 5000, "compression_ratio": 10}])
    assert r["chunks"] == 5000
    assert r["compression_ratio"] == 10.0
