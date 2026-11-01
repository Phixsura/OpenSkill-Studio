from app.services.app_marketplace_app_app_app_app_app_app_app_throughput_plan import plan_throughput, growth_plan

def test_plan():
    r = plan_throughput(target_rps=1000, avg_latency_ms=50, max_concurrent=100)
    assert r["concurrent_needed"] == 50
    assert r["instances_needed"] == 1
    assert r["headroom_pct"] > 0

def test_growth():
    plan = growth_plan(current_rps=100, growth_rate_pct=20, months=3)
    assert len(plan) == 3
    assert plan[0]["rps"] == 120
    assert plan[2]["rps"] > plan[0]["rps"]
