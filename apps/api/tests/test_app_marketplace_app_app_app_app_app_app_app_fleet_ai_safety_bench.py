from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_safety_bench import fleet_ai_safety_benchmark
def test_sb():
    r = fleet_ai_safety_benchmark([{"active": True, "tests": 50000, "pass_rate": 98.5, "categories": 20}])
    assert r["pass_rate"] == 98.5
    assert r["safe"]
