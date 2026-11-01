from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_mktplace_v2 import fleet_ai_marketplace_v2
def test_mv2():
    r = fleet_ai_marketplace_v2([{"active": True, "listings": 5000, "publishers": 1000, "installs_24h": 100000}])
    assert r["listings"] == 5000
    assert r["thriving"]
