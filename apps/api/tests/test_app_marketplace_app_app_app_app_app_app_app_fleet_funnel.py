from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_funnel import fleet_conversion_funnel
def test_funnel():
    r = fleet_conversion_funnel([{"name": "signup", "count": 1000}, {"name": "verify", "count": 500}, {"name": "activate", "count": 300}])
    assert r["overall_rate"] == 30.0
    assert r["worst_drop"]["step"] == "signup"
    assert r["healthy"]
