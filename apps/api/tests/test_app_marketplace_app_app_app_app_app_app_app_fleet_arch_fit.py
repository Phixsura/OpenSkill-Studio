from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_arch_fit import fleet_arch_fitness
def test_fit():
    r = fleet_arch_fitness([{"passed": True}] * 9 + [{"passed": False}])
    assert r["score"] == 90.0
    assert r["fit"]
