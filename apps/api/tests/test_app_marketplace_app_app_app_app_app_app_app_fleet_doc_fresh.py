from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_doc_fresh import fleet_doc_freshness
def test_fresh():
    r = fleet_doc_freshness([{"age_days": 30}, {"age_days": 60}, {"age_days": 120}])
    assert r["fresh"] == 2
    assert r["freshness_pct"] == 66.7
