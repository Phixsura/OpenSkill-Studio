from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_octant import fleet_octant_usage
def test_oct():
    r = fleet_octant_usage([{"active": True, "cluster": "prod"}, {"active": True, "cluster": "staging"}])
    assert r["active"] == 2
    assert r["clusters_viewed"] == 2
    assert not r["adopted"]
