from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dead_code import fleet_dead_code
def test_dead():
    r = fleet_dead_code([{"references": 5, "lines": 100}, {"references": 0, "lines": 50}])
    assert r["dead_files"] == 1
    assert r["dead_loc"] == 50
    assert not r["clean"]
