from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_value_stream import fleet_value_stream
def test_stream():
    r = fleet_value_stream([{"name": "dev", "cycle_time_hours": 40, "value_add_hours": 30, "wait_time_hours": 10},
                            {"name": "review", "cycle_time_hours": 20, "value_add_hours": 5, "wait_time_hours": 15}])
    assert r["efficiency_pct"] == 58.3
    assert r["bottleneck"] == "review"
