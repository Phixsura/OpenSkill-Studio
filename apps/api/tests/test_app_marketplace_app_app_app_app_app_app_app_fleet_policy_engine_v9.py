from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_policy_engine_v9 import fleet_policy_engine_v9
def test_pe_v9():
    r = fleet_policy_engine_v9([{"enforced": True, "violations": 0, "evals_per_sec": 5000}])
    assert r["enforced"] == 1
    assert r["violations"] == 0
    assert r["healthy"]
