from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_netlify import fleet_netlify_status
def test_ntl():
    r = fleet_netlify_status([{"published": True, "deploys_24h": 10, "functions": 15}])
    assert r["deploys_24h"] == 10
    assert r["all_published"]
