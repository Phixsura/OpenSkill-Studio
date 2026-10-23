from app.services.app_marketplace_app_app_app_app_app_app_app_capacity_plan import forecast_capacity, recommend_scaling

def test_forecast():
    r = forecast_capacity(50, 10, months=12, capacity_limit=100)
    assert r["current"] == 50
    assert len(r["projections"]) == 12
    assert r["final_usage"] > 50

def test_needs_expansion():
    r = forecast_capacity(80, 15, months=6, capacity_limit=100)
    assert r["needs_expansion"]
    assert r["months_to_limit"] is not None

def test_recommend():
    f = forecast_capacity(80, 20, months=12)
    r = recommend_scaling(f)
    assert r["action"] == "scale_up"
    assert r["recommended_capacity"] > 100
