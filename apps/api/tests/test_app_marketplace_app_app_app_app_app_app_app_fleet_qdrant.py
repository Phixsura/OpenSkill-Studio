from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_qdrant import fleet_qdrant_status
def test_qd():
    r = fleet_qdrant_status([{"status": "green", "points": 5000000}])
    assert r["total_points"] == 5000000
    assert r["healthy"]
