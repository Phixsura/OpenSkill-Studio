from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_seo import fleet_seo_score
def test_seo():
    r = fleet_seo_score([{"seo_score": 90}, {"seo_score": 85}, {"seo_score": 40}])
    assert r["avg_score"] == 71.7
    assert r["poor_pages"] == 1
    assert not r["good"]
