from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_db_repl import fleet_db_repl_lag
def test_repl():
    r = fleet_db_repl_lag([{"lag_ms": 50}, {"lag_ms": 100}, {"lag_ms": 2000}])
    assert r["max_lag_ms"] == 2000
    assert r["behind"] == 1
    assert not r["healthy"]
