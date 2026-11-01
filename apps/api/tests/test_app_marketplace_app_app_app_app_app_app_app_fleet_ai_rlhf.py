from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rlhf import fleet_ai_rlhf
def test_rlhf():
    r = fleet_ai_rlhf([{"active": True, "comparisons": 1000000, "reward_acc": 82, "ppo_steps": 50000}])
    assert r["comparisons"] == 1000000
    assert r["aligned"]
