from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_slow_query import fleet_slow_queries
def test_slow():
    r = fleet_slow_queries([{"duration_ms": 100}, {"duration_ms": 2000}, {"duration_ms": 6000}])
    assert r["slow"] == 2
    assert r["very_slow"] == 1
    assert r["needs_attention"]
