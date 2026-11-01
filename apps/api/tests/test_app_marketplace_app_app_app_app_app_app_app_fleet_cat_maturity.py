from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cat_maturity import fleet_catalog_maturity
def test_mat():
    r = fleet_catalog_maturity([{"has_owner": True, "has_docs": True, "has_runbook": True, "has_slo": True},
                                {"has_owner": True, "has_docs": False}])
    assert r["fully_cataloged"] == 1
    assert r["maturity_pct"] == 50.0
    assert not r["mature"]
