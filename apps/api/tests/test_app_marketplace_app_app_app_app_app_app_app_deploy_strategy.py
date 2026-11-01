from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_strategy import recommend_strategy, compare_strategies

def test_recommend():
    r = recommend_strategy({"zero_downtime": True, "fast_rollback": True})
    assert r["recommended"] == "blue_green"
    r2 = recommend_strategy({"traffic_splitting": True})
    assert r2["recommended"] == "canary"
    r3 = recommend_strategy({"zero_downtime": False})
    assert r3["recommended"] == "recreate"

def test_compare():
    r = compare_strategies("rolling", "canary")
    assert r["strategy_a"]["complexity"] == "low"
    assert r["strategy_b"]["complexity"] == "high"
