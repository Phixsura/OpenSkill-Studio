from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hpa_eff import fleet_hpa_effectiveness
def test_eff():
    r = fleet_hpa_effectiveness([{"scale_time_sec": 60}, {"scale_time_sec": 180}])
    assert r["responsive"] == 1
    assert r["avg_scale_time_sec"] == 120.0
    assert not r["effective"]
