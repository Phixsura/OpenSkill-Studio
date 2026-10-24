from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_docs import fleet_api_docs
def test_docs():
    r = fleet_api_docs([{"has_docs": True, "has_examples": True}, {"has_docs": True, "has_examples": False}, {"has_docs": False}])
    assert r["documented"] == 2
    assert r["coverage_pct"] == 66.7
    assert not r["complete"]
