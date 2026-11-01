from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_svc_catalog import fleet_svc_catalog
def test_catalog():
    r = fleet_svc_catalog([{"owner": "team-a", "has_docs": True, "has_runbook": True}, {"owner": "", "has_docs": False, "has_runbook": False}])
    assert r["with_owner"] == 1
    assert r["completeness_pct"] == 50.0
