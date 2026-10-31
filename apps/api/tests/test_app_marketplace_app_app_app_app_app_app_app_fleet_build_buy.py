from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_build_buy import fleet_build_vs_buy
def test_bb():
    r = fleet_build_vs_buy([{"source": "built"}, {"source": "bought"}, {"source": "oss"}, {"source": "built"}])
    assert r["built"] == 2
    assert r["build_ratio"] == 50.0
