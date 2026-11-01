from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vertex_ai import fleet_vertex_ai
def test_vai():
    r = fleet_vertex_ai([{"deployed": True, "models": 5, "predictions_24h": 2000000}])
    assert r["predictions_24h"] == 2000000
    assert r["all_deployed"]
