from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_toil import fleet_toil_summary
def test_toil():
    r = fleet_toil_summary([{"toil_hours": 10, "eng_hours": 30}, {"toil_hours": 20, "eng_hours": 40}])
    assert r["toil_hours"] == 30
    assert r["toil_pct"] == 30.0
    assert r["acceptable"]
