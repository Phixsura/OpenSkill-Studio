from app.services.app_marketplace_app_capacity_planner import forecast_usage, recommend_plan, compute_scaling_trigger

def test_forecast():
    f = forecast_usage(current=1000, growth_rate_pct=10, months=3)
    assert len(f) == 3
    assert f[0]["projected"] > 1000
    assert f[2]["projected"] > f[0]["projected"]

def test_recommend_free():
    r = recommend_plan(projected_api_calls=5000, projected_storage_gb=0.5)
    assert r["plan"] == "free"

def test_recommend_enterprise():
    r = recommend_plan(projected_api_calls=5000000, projected_storage_gb=500)
    assert r["plan"] == "enterprise"

def test_scale_needed():
    r = compute_scaling_trigger(current_load=90, max_capacity=100)
    assert r["should_scale"]
    assert r["recommended_capacity"] == 150

def test_no_scale():
    r = compute_scaling_trigger(current_load=50, max_capacity=100)
    assert not r["should_scale"]
