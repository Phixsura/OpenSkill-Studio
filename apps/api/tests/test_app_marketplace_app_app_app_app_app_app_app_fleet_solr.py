from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_solr import fleet_solr_status
def test_solr():
    r = fleet_solr_status([{"state": "active", "documents": 50000000, "qps": 10000}])
    assert r["documents"] == 50000000
    assert r["all_active"]
