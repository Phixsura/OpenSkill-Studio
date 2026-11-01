from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_evolution import fleet_evolution
def test_evo():
    r = fleet_evolution([{"files": 100}, {"files": 500}, {"files": 1000}])
    assert r["growth_pct"] == 900.0
    assert r["accelerating"]
