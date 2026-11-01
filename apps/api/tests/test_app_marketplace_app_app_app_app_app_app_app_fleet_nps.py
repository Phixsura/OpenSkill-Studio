from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nps import fleet_platform_nps
def test_nps():
    r = fleet_platform_nps([{"score": 10}, {"score": 9}, {"score": 7}, {"score": 5}])
    assert r["promoters"] == 2
    assert r["detractors"] == 1
    assert r["nps"] == 25.0
